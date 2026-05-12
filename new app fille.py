# --- OUTREACH SECTION (Advanced & Stable) ---
        st.divider()
        st.markdown("### ✉️ Fast-Track Communication")
        
        # Candidate selection
        select_c = st.selectbox("Pick a candidate to notify:", df["Name"].unique())
        c_info = df[df["Name"] == select_c].iloc[0]

        # Input fields for contact
        c1, c2 = st.columns(2)
        with c1:
            e_mail = st.text_input("Target Email", c_info["Email"])
            p_hone = st.text_input("Target WhatsApp", c_info["Phone"])
        with c2:
            status_msg = "shortlisted" if "✅" in c_info["Status"] else "not selected"
            msg_body = f"Hello {select_c}!\n\nThis is regarding your application. We have reviewed your profile and you are {status_msg} for the next round.\n\nRegards,\nHR Team"
            final_msg = st.text_area("Message Preview", msg_body)

        # Action Buttons
        b1, b2 = st.columns(2)
        with b1:
            # WhatsApp Link
            wa_link = f"https://wa.me/{p_hone.replace('+', '')}?text={quote(final_msg)}"
            st.link_button("📱 WhatsApp Candidate", wa_link, use_container_width=True)
            
        with b2:
            # Email Link (Using official st.link_button for stability)
            subject = quote("Job Application Update")
            body = quote(final_msg)
            mail_link = f"mailto:{e_mail}?subject={subject}&body={body}"
            st.link_button("📧 Send Email Now", mail_link, use_container_width=True)

        st.success(f"Tip: Email button will open your default app (Gmail/Outlook). Check if your browser blocks popups!")
