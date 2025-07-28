
import os
import streamlit as st
from typing import Optional, Union

from llama_index.llms.openai import OpenAI
from llama_index.graph_stores.neo4j import Neo4jPropertyGraphStore
from llama_index.core import PropertyGraphIndex

from llama_index.core.retrievers import (
    CustomPGRetriever,
    VectorContextRetriever,
    TextToCypherRetriever,
)
from llama_index.core.vector_stores.types import VectorStore
from llama_index.core.embeddings import BaseEmbedding
from llama_index.core.prompts import PromptTemplate
from llama_index.core.llms import LLM
from llama_index.core.postprocessor import LLMRerank
from llama_index.core.query_engine import RetrieverQueryEngine

class IYPRetriever(CustomPGRetriever):

    def init(
        self,
        ## vector context retriever params
        embed_model: Optional[BaseEmbedding] = None,
        vector_store: Optional[VectorStore] = None,
        similarity_top_k: int = 4,
        path_depth: int = 1,
        ## text-to-cypher params
        llm: Optional[LLM] = None,
        text_to_cypher_template: Optional[Union[PromptTemplate, str]] = None,
        custom_cypher_query: Optional[str] = None,
        cypher_limit: Optional[int] = None,
        ## reranker params
        reranker_top_n: int = 2,
    ) -> None:
        
        self.vector_retriever = VectorContextRetriever(
            self.graph_store,
            include_text=self.include_text,
            embed_model=embed_model,
            vector_store=vector_store,
            similarity_top_k=similarity_top_k,
            path_depth=path_depth,
        )

        self.cypher_retriever = TextToCypherRetriever(
            self.graph_store,
            llm=llm,
            text_to_cypher_template=text_to_cypher_template,
            cypher_limit=cypher_limit,
            custom_cypher_query=custom_cypher_query,
            include_raw_response_as_metadata=True
        )

        self.reranker = LLMRerank(
            choice_batch_size=5,
            top_n=reranker_top_n
        )

        self.generated_cypher_query = None
        self.query_output = None

    def custom_retrieve(self, query_str: str) -> str:
        nodes_1 = self.vector_retriever.retrieve(query_str)
        nodes_2 = self.cypher_retriever.retrieve(query_str)

        self.generated_cypher_query = self.cypher_retriever.generated_cypher_query
        self.query_output = self.cypher_retriever.query_output

        reranked_nodes = self.reranker.postprocess_nodes(
            nodes_1 + nodes_2, query_str=query_str
        )

        final_text = "\n\n".join(
            [n.get_content(metadata_mode="llm") for n in reranked_nodes]
        )

        return final_text


@st.cache_resource(show_spinner=False)
def init_chatiyp_model():

    # Connect to Neo4j IYP graph
    llm = OpenAI(model="gpt-3.5-turbo", temperature=0.3)

    graph_store = Neo4jPropertyGraphStore(
        username="neo4j",
        password="password",
        url="bolt://iyp:7687",
        database="neo4j"
    )

    index = PropertyGraphIndex.from_existing(
        property_graph_store=graph_store
    )

    sub_retriever = IYPRetriever(
        index.property_graph_store,
        vector_store=index.vector_store,
        cypher_limit=10,
    )

    query_engine = RetrieverQueryEngine.from_args(
        index.as_retriever(sub_retrievers=[sub_retriever]), llm=llm
    )

    return query_engine, sub_retriever