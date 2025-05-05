import streamlit as st
from supabase import create_client
import pandas as pd

# ------------------------------------------------------
# Configuración página y conexión
# ------------------------------------------------------
st.set_page_config(page_title="Registro de Actividad", layout="wide")
URL = "https://juezcuepljxpsiqgatyb.supabase.co"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imp1ZXpjdWVwbGp4cHNpcWdhdHliIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDY0MTcyNTIsImV4cCI6MjA2MTk5MzI1Mn0.N1uSwnN0DydpLtMVp_XSD3JHWjaJbEbUyUTrfTVmn54"
supabase = create_client(URL, KEY)


st.title("📋 Registro de Actividad")

# ------------------------------------------------------
# Formulario para nueva actividad
# ------------------------------------------------------
with st.form("nueva_actividad"):
    c1, c2, c3 = st.columns([2,4,4])
    with c1:
        activity_date = st.date_input("Fecha")
    with c2:
        activity = st.text_input("Actividad")
    with c3:
        category = st.text_input("Categoría")
    notes = st.text_area("Notas (opcional)")
    enviar = st.form_submit_button("Guardar actividad")

if enviar:
    record = {
        "activity_date": activity_date.isoformat(),
        "activity":      activity,
        "category":      category,
        "notes":         notes
    }
    res = supabase.from_("activities").insert(record).execute()
    if getattr(res, "status_code", 0) >= 400:
        st.error("Error al guardar la actividad")
    else:
        st.success("Actividad registrada ✔️")

st.markdown("---")

# ------------------------------------------------------
# Carga y filtro de actividades
# ------------------------------------------------------
all_acts = supabase.from_("activities")\
    .select("id,activity_date,activity,category,notes")\
    .order("activity_date", desc=False).execute().data or []
df_acts = pd.DataFrame(all_acts)
if df_acts.empty:
    st.info("Aún no hay actividades registradas.")
    st.stop()

df_acts["activity_date"] = pd.to_datetime(df_acts["activity_date"]).dt.date

# Sidebar: selecciona día
day = st.sidebar.date_input("Ver actividad de")
df_day = df_acts[df_acts["activity_date"] == day]

st.subheader(f"Actividades del {day}")
if df_day.empty:
    st.write("— Ninguna actividad para este día —")
else:
    for _, row in df_day.iterrows():
        cols = st.columns([1,4,2,4,1], gap="small")
        cols[0].write(row["id"])
        cols[1].write(row["activity"])
        cols[2].write(row["category"] or "—")
        cols[3].write(row["notes"] or "—")
        if cols[4].button("Eliminar", key=f"del_act_{row['id']}"):
            supabase.from_("activities").delete().eq("id", row["id"]).execute()
            st.success("Actividad eliminada ✔️")
