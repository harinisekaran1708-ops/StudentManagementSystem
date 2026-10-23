
import streamlit as st
import psycopg

st.title("Student Database Connectivity")

password = st.text_input("PostgreSQL Password", type="password")

name = st.text_input("Enter Student Name")
department = st.text_input("Enter Department")
marks = st.number_input("Enter Marks", 0, 100, 0)

if st.button("Insert Student"):
    if not password or not name.strip() or not department.strip():
        st.warning("Enter password, name and department.")
    else:
        try:
            with psycopg.connect(
                host="localhost",
                port=5432,
                dbname="college_db",
                user="postgres",
                password=password
            ) as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO students (name, department, marks)
                        VALUES (%s, %s, %s)
                    """, (name.strip(), department.strip(), marks))

            st.success("Student inserted successfully!")

        except Exception as e:
            st.error(f"Error: {e}")

if st.button("Display Students"):
    if not password:
        st.warning("Enter your PostgreSQL password first.")
    else:
        try:
            with psycopg.connect(
                         host="localhost",
                         port=5432,
                         dbname="College_db",
                         user="postgres",
                         password=password

            ) as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT * FROM students")
                    rows = cur.fetchall()

            st.subheader("Student Records")
            st.dataframe(
                rows,
                column_config={
                    0: "ID",
                    1: "Name",
                    2: "Department",
                    3: "Marks"
                },
                hide_index=True
            )

        except Exception as e:
            st.error(f"Error: {e}")
