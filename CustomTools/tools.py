from abc import ABC, abstractmethod
import requests
import justext

import streamlit as st

from langchain.chains import RetrievalQA
from langchain.chains.summarize import load_summarize_chain
from Serp.serp import CustomSerpAPIWrapper
from langchain.agents import load_tools


class CustomTool(ABC):
    @abstractmethod
    def run(self, query: str):
        pass


class SummarizationTool(CustomTool):
    def __init__(self, llm, document_chunks):
        self.chain = load_summarize_chain(llm, chain_type="map_reduce")
        self.document_chunks = document_chunks

    def run(self, query: str):
        return self.run_chain()

    @st.cache
    def run_chain(self):
        return self.chain.run(self.document_chunks)


class LookupTool(CustomTool):
    def __init__(self, llm, vector_store):
        self.retrieval = RetrievalQA.from_chain_type(
            llm=llm, chain_type="stuff", retriever=vector_store.as_retriever(),
            return_source_documents=True
        )

    def run(self, query: str):
        res = self.retrieval(query)
        st.session_state.doc_sources = res['source_documents']
        return res['result']


class ArxivTool(CustomTool):
    def __init__(self, llm):
        self.arxiv = load_tools(["arxiv"], llm=llm)[0]

    def run(self, query: str):
        response = self.arxiv.run(query)
        st.session_state.google_sources.append(response)
        return response
