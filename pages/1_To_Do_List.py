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
# 1) Cargo actividades pendientes
# ------------------------------------------------------
pending = (
    supabase
      .from_("activities")
      .select("id,activity,category,notes")
      .eq("activity_date", day.isoformat())
      .order("id", desc=False)
      .execute()
      .data
) or []
df_pending = pd.DataFrame(pending)

# ------------------------------------------------------
# 2) Cargo actividades completadas
# ------------------------------------------------------
done = (
    supabase
      .from_("completed_activities")
      .select("id,activity,category,notes,completed_at")
      .eq("activity_date", day.isoformat())
      .order("completed_at", desc=False)
      .execute()
      .data
) or []
df_done = pd.DataFrame(done)

# ------------------------------------------------------
# 3) Si no hay ninguna actividad
# ------------------------------------------------------
if df_pending.empty and df_done.empty:
    st.info(f"No hay actividades para el {day}.")
    st.stop()

# ------------------------------------------------------
# 4) Mostrar pendientes en formato tabla
# ------------------------------------------------------
st.subheader(f"Actividades para {day}")
st.markdown("**Pendientes**")

# Encabezados
h1, h2, h3, h4 = st.columns([4,2,4,1], gap="small")
h1.markdown("**Actividad**")
h2.markdown("**Categoría**")
h3.markdown("**Notas**")
h4.markdown("**Acción**")

if df_pending.empty:
    st.write("— Ninguna pendiente —")
else:
    for _, row in df_pending.iterrows():
        c1, c2, c3, c4 = st.columns([4,2,4,1], gap="small")
        c1.write(row["activity"])
        c2.write(row.get("category") or "—")
        c3.write(row.get("notes")    or "—")
        if c4.button("Completada", key=f"done_{row['id']}"):
            # 1) Mover a completed_activities
            supabase.from_("completed_activities").insert({
                "activity_date": day.isoformat(),
                "activity":      row["activity"],
                "category":      row.get("category"),
                "notes":         row.get("notes")
            }).execute()
            # 2) Eliminar de activities
            supabase.from_("activities").delete().eq("id", row["id"]).execute()
            st.success("Actividad marcada como completada")
            # No hace falta código extra: Streamlit recarga automáticamente

# ------------------------------------------------------
# 5) Mostrar completadas con opción Revertir
# ------------------------------------------------------
st.markdown("---")
st.markdown("**Completadas**")

if df_done.empty:
    st.write("— Ninguna completada —")
else:
    # Formatear fecha de completado
    df_done["Completada el"] = pd.to_datetime(df_done["completed_at"])\
                                  .dt.strftime("%Y-%m-%d %H:%M:%S")
    # Encabezados
    h1, h2, h3, h4 = st.columns([4,2,4,1], gap="small")
    h1.markdown("**Actividad**")
    h2.markdown("**Categoría**")
    h3.markdown("**Notas**")
    h4.markdown("**Acción**")
    # Filas
    for _, row in df_done.iterrows():
        c1, c2, c3, c4 = st.columns([4,2,4,1], gap="small")
        c1.write(row["activity"])
        c2.write(row.get("category") or "—")
        c3.write(row.get("notes")    or "—")
        if c4.button("Revertir", key=f"undo_{row['id']}"):
            # 1) Volver a activities
            supabase.from_("activities").insert({
                "activity_date": day.isoformat(),
                "activity":      row["activity"],
                "category":      row.get("category"),
                "notes":         row.get("notes")
            }).execute()
            # 2) Eliminar de completed_activities
            supabase.from_("completed_activities").delete().eq("id", row["id"]).execute()
            st.success("Actividad revertida a pendientes")
            # Nuevamente, la recarga es automática al pulsar el botón
