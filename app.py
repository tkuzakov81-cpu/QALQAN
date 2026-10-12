
                A useful detector should catch suspicious messages while avoiding
                too many false alarms.
                """
            )

        st.markdown("### Individual test results")
        st.dataframe(
            df[["Category", "Expected", "Predicted", "Score", "Outcome"]],
            use_container_width=True,
            hide_index=True,
        )

        with st.expander("View the full test messages"):
            st.dataframe(
                df[["Category", "Message", "Expected", "Predicted", "Score"]],
                use_container_width=True,
                hide_index=True,
            )

        st.markdown("### What to improve next")

        if fp > 0:
            st.warning(
                f"QALQAN raised {fp} false alarm(s). "
                "Review these ordinary messages and adjust overly broad rules."
            )
        else:
            st.success("No false alarms in this small test set.")

        if fn > 0:
            st.warning(
                f"QALQAN missed {fn} suspicious message(s). "
                "Review their wording and add useful variations to the rules."
            )
        else:
            st.success("All suspicious examples in this test set were detected.")

        st.caption(
            "This test set is small and hand-written. "
            "For stronger evaluation, test more realistic messages that were "
            "not used while designing the rules."
        )


# --------------------------------------------------
# About QALQAN
# --------------------------------------------------

elif page == "💡 About QALQAN":
    st.markdown(
        """
        <div class="hero">
            <div class="eyebrow">About the project</div>
            <div class="hero-title">QALQAN protects through awareness.</div>
            <div class="hero-copy">
                A student-built prototype that helps people recognize
                suspicious messages and understand common online safety risks.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### The idea")
    st.markdown(
        """
        Online scams often use familiar patterns: urgent demands, unexpected
        prizes, suspicious payment requests, and attempts to collect private data.

        QALQAN checks message text against warning phrases, calculates a
        suspicion score, and explains which patterns were found.
        """
    )

    st.markdown("### What the prototype can do")
    st.markdown(
        """
        - Analyze pasted text using phrase-matching rules.
        - Explain detected warning signs.
        - Offer basic safety recommendations.
        - Run a labeled test set and display evaluation metrics.
        """
    )

    st.markdown("### Current limitations")
    st.markdown(
        """
        - It uses rules, not a trained machine-learning model.
        - It may miss unfamiliar wording, slang, or new scam techniques.
        - It may flag harmless messages containing suspicious phrases.
        - Its score is a heuristic, not a verified probability of fraud.
        - The built-in test set is small and cannot represent every real-world message.
        """
    )

    st.info(
        "QALQAN is a learning and awareness tool. "
        "When a message asks for money, passwords, or verification codes, "
        "verify it through an independent official channel."
    )


# --------------------------------------------------
# Footer
# --------------------------------------------------

st.markdown(
    """
    <div class="footer">
        QALQAN · Creative Lab · Think twice. Click wisely.
    </div>
    """,
    unsafe_allow_html=True,
)
