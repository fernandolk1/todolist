# pages/05_ToDo_List.py

import streamlit as st
from supabase import create_client
import pandas as pd
from datetime import date

# ------------------------------------------------------
# Configuración y conexión
# ------------------------------------------------------
st.set_page_config(page_title="To-Do List", layout="wide")
URL = "https://juezcuepljxpsiqgatyb.supabase.co"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imp1ZXpjdWVwbGp4cHNpcWdhdHliIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDY0MTcyNTIsImV4cCI6MjA2MTk5MzI1Mn0.N1uSwnN0DydpLtMVp_XSD3JHWjaJbEbUyUTrfTVmn54"
supabase = create_client(URL, KEY)



st.title("✅ To-Do List desde Actividades")

# ------------------------------------------------------
# Sidebar: filtro por fecha
# ------------------------------------------------------
day = st.sidebar.date_input("Ver actividades de", value=date.today())

# ------------------------------------------------------
# 1) Cargo actividades pendientes de esa fecha
# ------------------------------------------------------
acts = (
    supabase.from_("activities")
             .select("id,activity")
             .eq("activity_date", day.isoformat())
             .order("id", desc=False)
             .execute().data
) or []
df_pending = pd.DataFrame(acts)

# ------------------------------------------------------
# 2) Cargo actividades ya completadas
# ------------------------------------------------------
comp = (
    supabase.from_("completed_activities")
             .select("activity,completed_at")
             .eq("activity_date", day.isoformat())
             .order("completed_at", desc=False)
             .execute().data
) or []
df_done = pd.DataFrame(comp)

# ------------------------------------------------------
# 3) Si no hay ninguna actividad en ambas tablas
# ------------------------------------------------------
if df_pending.empty and df_done.empty:
    st.info(f"No hay actividades para el {day}.")
    st.stop()

# ------------------------------------------------------
# 4) Mostrar pendientes
# ------------------------------------------------------
st.subheader(f"Actividades para {day}")
st.markdown("**Pendientes**")
if df_pending.empty:
    st.write("— Ninguna pendiente —")
else:
    for _, row in df_pending.iterrows():
        c1, c2 = st.columns([4,1], gap="small")
        c1.write(row["activity"])
        if c2.button("Completada", key=f"done_{row['id']}"):
            # 1) Inserto en completed_activities
            supabase.from_("completed_activities").insert({
                "activity_date": day.isoformat(),
                "activity":      row["activity"],
                "category":      None,
                "notes":         "Completada desde To-Do"
            }).execute()
            # 2) Borro de activities
            supabase.from_("activities").delete().eq("id", row["id"]).execute()
            st.success("Actividad marcada como completada")
            # ya no revertimos ni recargamos automáticamente

# ------------------------------------------------------
# 5) Mostrar completadas
# ------------------------------------------------------
st.markdown("---")
st.markdown("**Completadas**")
if df_done.empty:
    st.write("— Ninguna completada —")
else:
    df_done["completed_at"] = pd.to_datetime(df_done["completed_at"])
    df_done["Hora"] = df_done["completed_at"].dt.strftime("%H:%M:%S")
    st.table(
        df_done[["activity", "Hora"]]
        .rename(columns={"activity":"Actividad"})
    )
