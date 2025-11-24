import time
from datetime import datetime
from os import getenv

import pandas as pd
import requests
import streamlit as st

# pass
# API_URL: str = "http://localhost:8000"
# API_URL: str = "http://127.0.0.1:8000"
API_URL: str = getenv("API_URL", default="http://127.0.0.1:8000")
REFRESH_INTERVAL: int = 5  # seconds


def highlight_anomalies(row: pd.Series):
    if "is_anomaly" in row and row["is_anomaly"]:
        return ["background-color: rgba(255, 0, 0, 0.2)"] * len(row)
    else:
        return [""] * len(row)


st.set_page_config(
    page_title="Anomaly Monitor in windmill factory (IUBH)",
    layout="wide",
)

st.title("Anomaly Monitor Dashboard")
st.caption(f"API at {API_URL}")
st.caption(f"with /status, /score, /recent_scores")

st.sidebar.header("System Health")


def check_status():
    try:
        resp = requests.get(f"{API_URL}/status", timeout=3)
        if resp.status_code == 200:
            st.sidebar.success("API online")
            st.sidebar.json(resp.json())
    except requests.exceptions.RequestException as e:
        st.sidebar.error(" API problems")
        st.sidebar.write(f"{e}")
    except Exception as e:
        st.sidebar.write(f"general error: {e}")


if st.sidebar.button("Refresh status"):
    check_status()
else:
    check_status()

st.sidebar.markdown("---")
st.sidebar.caption("dashboard (streamlit) connected to FastAPI (/status, /score)")

if "history" not in st.session_state:
    st.session_state.history = []

col_left, col_right = st.columns(2)

with col_left:
    st.subheader("Manual requests")
    st.write("Use to send 1 datum to API and inspect prediction")

    c_temp = st.slider("Temperature (°C)", min_value=-20, max_value=120, value=21)
    c_humid = st.slider("Humidity (%)", min_value=0, max_value=100, value=60)
    c_sound = st.slider("Sound (dB)", min_value=0, max_value=140, value=50)

    if st.button("Analyze current datum"):
        payload = {
            "temperature_c": float(c_temp),
            "humidity_pct": float(c_humid),
            "sound_db": float(c_sound),
        }
        try:
            resp = requests.post(f"{API_URL}/score", json=payload, timeout=3)
            if resp.status_code != 200:
                st.error(f" API ERROR: {resp.status_code}")
                st.code(resp.text)
            else:
                data = resp.json()

                m1, m2, m3 = st.columns(3)
                m1.metric("Temperature", f"{c_temp} °C")
                m2.metric("Humidity", f"{c_humid} %")
                m3.metric("Sound", f"{c_sound} dB")

                is_anomaly = data.get("is_anomaly", False)
                score = data.get("anomaly_score", 0.0)
                status_text = data.get("status", "Unknown")

                if is_anomaly:
                    st.error(f"ANOMALY!!! {status_text} (Score: {score:.3f}")
                else:
                    st.success(f"All is normal, {status_text} (score: {score:.3f})")

                st.session_state.history.append(
                    {
                        "timestamp (UTC)": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "temperature_c": c_temp,
                        "humidity_pct": c_humid,
                        "sound_db": c_sound,
                        "is_anomaly": is_anomaly,
                        "anomaly_score": score,
                    }
                )
        except requests.exceptions.RequestException as e:
            st.error(f" API error: {e}")
        except Exception as e:
            st.error(f"General error: {e}")

with col_right:
    st.subheader("History & live tracking from API (UTC time)")
    live_mode = st.checkbox(
        f"Auto-update (every {REFRESH_INTERVAL} seconds)", value=True
    )

    chart_placeholder = st.empty()
    table_placeholder = st.empty()

    def render_live_view():
        try:
            resp = requests.get(f"{API_URL}/recent_scores?limit=50", timeout=2)
            if resp.status_code == 200:
                recent = resp.json()
                if recent:
                    df_live = pd.DataFrame(recent)
                    df_live["timestamp"] = pd.to_datetime(df_live["timestamp"])
                    df_live = df_live.set_index("timestamp")

                    chart_placeholder.line_chart(df_live["anomaly_score"])

                    # table_placeholder.markdown("#### Latest events (UTC)")

                    df_latest = df_live.sort_index(ascending=False).head(50)
                    red_latest = df_latest.style.apply(highlight_anomalies, axis=1)

                    # st.dataframe(
                    #    red_latest,
                    #    width="stretch",
                    # )
                    with table_placeholder.container():
                        st.markdown("#### Latest events (UTC) / live")
                        st.dataframe(
                            red_latest,
                            width="stretch",
                            height=600,
                        )

                    # table_placeholder.dataframe(
                    #    df_live.sort_index(ascending=False).head(50),
                    #    width="stretch",
                    # )
                else:
                    chart_placeholder.empty()
                    table_placeholder.info(
                        "No recent scores yet. Connect stream (sim) to see live data."
                    )
            else:
                chart_placeholder.empty()
                table_placeholder.error(
                    f"Could not fetch recent scores: {resp.status_code}"
                )
        except requests.exceptions.RequestException as e:
            chart_placeholder.empty()
            table_placeholder.error("API Error (recent scores).")
            table_placeholder.write(str(e))

    if live_mode:
        # Simple auto-refresh loop; stop via the "Stop" button in Streamlit UI
        while True:
            render_live_view()
            time.sleep(REFRESH_INTERVAL)
    else:
        # Single snapshot
        render_live_view()

    st.markdown("---")
    st.subheader("Manual requests history")
    if st.session_state.history:
        df = pd.DataFrame(st.session_state.history)
        df_display = df.iloc[::-1].reset_index(drop=True)
        st.dataframe(
            df_display,
            width="stretch",
            hide_index=True,
        )
    else:
        st.info("No manual checks yet. Use the btn on the left.")

st.markdown("---")
st.caption(
    "API health via `/status`, "
    "and model behaviour via manual probes to `/score` with a history of anomaly scores."
)
