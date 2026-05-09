"""FlowPilot Web UI — Streamlit application."""

from __future__ import annotations

import asyncio
import sys

import streamlit as st

# Ensure project root is on path when running directly
from flowpilot.config import Config
from flowpilot.rag import DocumentLoader, Retriever
from flowpilot.orchestrator import DevFlow


def get_config() -> Config:
    return Config(
        api_key=st.session_state.get("api_key", ""),
        base_url=st.session_state.get("base_url", "https://api.openai.com/v1"),
        model=st.session_state.get("model", "gpt-4o"),
    )


def init_session():
    defaults = {
        "messages": [],
        "api_key": "",
        "base_url": "https://api.openai.com/v1",
        "model": "gpt-4o",
        "rag_chunks": 0,
        "rag_docs": 0,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def render_sidebar():
    with st.sidebar:
        st.header("Settings")

        st.session_state.api_key = st.text_input("API Key", type="password", value=st.session_state.api_key)
        st.session_state.base_url = st.text_input("Base URL", value=st.session_state.base_url)
        st.session_state.model = st.text_input("Model", value=st.session_state.model)

        st.divider()
        st.subheader("Knowledge Base (RAG)")
        uploaded_files = st.file_uploader(
            "Upload documents",
            type=["txt", "md", "py", "js", "ts", "json", "yaml", "csv"],
            accept_multiple_files=True,
        )
        if uploaded_files and st.button("Index Documents"):
            config = get_config()
            if not config.api_key:
                st.error("Please set API Key first")
            else:
                with st.spinner("Indexing documents..."):
                    retriever = Retriever()
                    loop = asyncio.new_event_loop()
                    try:
                        for f in uploaded_files:
                            content = f.read().decode("utf-8")
                            loop.run_until_complete(retriever.add_text(content, source=f.name))
                    finally:
                        loop.close()
                    st.session_state.rag_chunks = retriever.chunk_count
                    st.session_state.rag_docs = retriever.document_count
                    st.session_state.retriever = retriever
                st.success(f"Indexed {st.session_state.rag_docs} docs ({st.session_state.rag_chunks} chunks)")

        if st.session_state.rag_chunks > 0:
            st.info(f"{st.session_state.rag_docs} docs | {st.session_state.rag_chunks} chunks")

        st.divider()
        mode = st.selectbox("Mode", ["full", "plan", "code", "review", "test"], format_func=lambda x: {
            "full": "Full Pipeline",
            "plan": "Plan Only",
            "code": "Code Only",
            "review": "Review Only",
            "test": "Test Only",
        }[x])
        st.session_state.mode = mode


def render_chat():
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Describe your requirement..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        config = get_config()
        if not config.api_key:
            with st.chat_message("assistant"):
                st.error("Please set API Key in sidebar")
            return

        retriever = st.session_state.get("retriever")
        flow = DevFlow(config=config, retriever=retriever)

        with st.chat_message("assistant"):
            with st.spinner("Running agent pipeline..."):
                try:
                    loop = asyncio.new_event_loop()
                    result = loop.run_until_complete(
                        flow.run(prompt, mode=st.session_state.get("mode", "full"))
                    )
                    loop.close()
                except Exception as e:
                    st.error(f"Error: {e}")
                    return

            tabs = []
            tab_names = []
            if result.plan:
                tab_names.append("Plan")
            if result.code:
                tab_names.append("Code")
            if result.review:
                tab_names.append("Review")
            if result.tests:
                tab_names.append("Tests")

            if tab_names:
                tabs = st.tabs(tab_names)
                idx = 0
                if result.plan:
                    with tabs[idx]:
                        st.markdown(result.plan)
                    idx += 1
                if result.code:
                    with tabs[idx]:
                        st.code(result.code, language="python")
                    idx += 1
                if result.review:
                    with tabs[idx]:
                        st.markdown(result.review)
                    idx += 1
                if result.tests:
                    with tabs[idx]:
                        st.code(result.tests, language="python")
                    idx += 1

            response_text = result.report
            st.session_state.messages.append({"role": "assistant", "content": response_text})


def main():
    st.set_page_config(page_title="FlowPilot", page_icon="🚀", layout="wide")
    st.title("FlowPilot")
    st.caption("Multi-Agent Development Workflow")

    init_session()
    render_sidebar()
    render_chat()


if __name__ == "__main__":
    main()
