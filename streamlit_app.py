# -*- coding: utf-8 -*-
# Copyright 2018-2022 Streamlit Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.CO

import os
import numpy as np
import pandas as pd

import requests
import json

import streamlit as st


def is_blank(my_string: str) -> bool:
    return not (my_string and my_string.strip())


@st.cache_data
def crida_api(tipus: str, document: str):
    url = "https://fcoc.playoffinformatica.com/api.php/api/v1.0/llicencies/persones?"
    match tipus:
        case "DNI/NIE":
            website = f"{url}nif={document}"
        case "PASSAPORT":
            website = f"{url}residencia={document}"
        case "CATSALUT":
            website = f"{url}catsalut={document}"
        case _:
            website = ""
    if not is_blank(website):
        opcions = {"Authorization": f"Bearer {os.getenv('FCOC_PLAYOFF_API_TOKEN')}", "Content-Type": "application/json"}
        resposta = requests.get(url=website, headers=opcions)
        if resposta.ok:
            return resposta.json()
        else:
            # return f"Error {website} request: {resposta.status_code}"
            return []
    else:
        return []


class Llicencia:
    def __init__(self, llicencia: dict):
        self.codi = llicencia.get("codiLlicencia", "-")
        self.estat = llicencia.get("estatLlicencia", "-")

        federat = llicencia.get("federat", {})
        persona = federat.get("persona", {})
        self.esportista = f"{persona.get('cognoms', '-')}, {persona.get('nom', '-')}"

        club = llicencia.get("club", {})
        self.club = club.get("nom", "-")

        modalitat = llicencia.get("modalitatLlicencia", {})
        self.llic_tipus = int(modalitat.get("idModalitat", "-99")) # ens interessen les que son 1 (= Esportista)

        temporada = modalitat.get("temporadaLlicencia", {})
        self.temporada = temporada.get("nom", "-")

        categoria = modalitat.get("categoriaLlicencia", {})
        subcategoria = categoria.get("subCategoriaLlicencia", {})

        self.llic_nom = f"{categoria.get('nom', '-')} | {subcategoria.get('nom', '-')}"


    def is_esportista(self):
        if self.llic_tipus == 1:
            return True
        else:
            return False


    def is_tramitada(self):
        if self.estat == "LLIESTTRA":
            return True
        else:
            return False


def streamlit_main():
    # SETTING PAGE CONFIG TO WIDE MODE AND ADDING A TITLE AND FAVICON (1rst sentence Streamlit!!!)
    st.set_page_config(layout="wide", page_title="FCOC - consulta Llicencia", page_icon=":earth:")

    row1_1, row1_2 = st.columns((0.5,3))
    row1_1.image("logo_fcoc_2q.png", caption="", use_column_width=True)
    row1_2.title("Consulta llicencia FCOC")
    with row1_2.expander("About"):
        st.write("Permet comprobar si un esportista disposa de llicència federativa tramitada.")
        st.write("Cal introduir alguna d'aquestes dades: DNI/NIE, passaport o CATSALUT.")

    row2_1, row2_2 = st.columns((1, 3))

    row2_1.subheader(f"Select...")
    # escollim si entrem DNI/NIE, passaport o CATSALUT
    tipus = row2_1.selectbox("Escull una de les opcions:", ["DNI/NIE", "PASSAPORT", "CATSALUT"])
    document = row2_1.text_input(f"Entra {tipus}: ")

    if is_blank(document):
        row2_2.write("")
    else:
        llicencies = crida_api(tipus, document)
        row2_2.write(f"Num. llicències trobades: {len(llicencies)}")
        nllic = 0
        for llic_dict in llicencies:
            nllic += 1
            llic = Llicencia(llic_dict)
            if llic.is_esportista():
                # anem a mirar quin es l'estat:
                if llic.is_tramitada():
                    row2_2.write(f"LLicència {nllic} ------")
                    row2_2.write(f"Codi: {llic.codi}")
                    row2_2.write(f"Esportista: {llic.esportista}")
                    row2_2.write(f"Club: {llic.club}")
                    row2_2.write(f"Tipus: {llic.temporada} | {llic.llic_nom}")
                else:
                    match llic.estat:
                        case "LLIESTPRE":
                            estat = "PREinscrita"
                        case "LLIESTVAL":
                            estat = "VALidada"
                        case "LLIESTFAC":
                            estat = "FACturada"
                        case "LLIESTTRA":
                            estat = "TRAmitada"
                        case "LLIESTANU":
                            estat = "ANUl.lada"
                        case _:
                            estat = "???"
                    row2_2.write(f" Llicència {nllic} - no està tramitada. Estat: {estat} ({llic.estat})")
            else:
                row2_2.write(f" Llicència {nllic } - no és de tipus Esportista")

# ---------------------------------------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------------------------
if __name__ == '__main__':
    streamlit_main()
