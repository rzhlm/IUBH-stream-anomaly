import time
from datetime import datetime

import pandas as pd
import requests
import streamlit as st

# pass
API_URL: str = "http://localhost:8000"
REFRESH_INTERVAL: int = 5

st.set_page_config(
    page_title="Anomaly Monitor in windmill factory (IUBH)",
    layout="wide",
)

st.title("Anomaly Monitor Dashboard")
st.caption(f"API at {API_URL}")

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
    st.write("Use here to send 1 datum to API and inspect prediction")

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
                    st.success(f"All is normal,  {status_text} (Score: {score:.3f}")

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
    st.subheader("History from API")

    try:
        resp = requests.get(f"{API_URL}/recent_scores?limit=15", timeout=2)
        if resp.status_code == 200:
            recent = resp.json()
            if recent:
                df_live = pd.DataFrame(recent)
                df_live["timestamp"] = pd.to_datetime(df_live["timestamp"])
                df_live = df_live.set_index("timestamp")

                # Line chart of anomaly scores over time
                st.line_chart(df_live["anomaly_score"])

                st.markdown("#### Latest events (in UTC)")
                st.dataframe(
                    df_live.sort_index(ascending=False).head(50),
                    width="stretch",
                )
            else:
                st.info("No recent scores yet. Connect stream (sim) to see live data.")
        else:
            st.error(f"Could not fetch recent scores: {resp.status_code}")
            st.write(resp.text)
    except requests.exceptions.RequestException as e:
        st.error("API error.")
        st.write(str(e))
    except Exception as e:
        st.error("General error:")
        st.write(str(e))

    st.markdown("---")
    st.subheader(" manual queries: ")
    if st.session_state.history:
        df = pd.DataFrame(st.session_state.history)
        df_display = df.iloc[::-1].reset_index(drop=True)  # most recent shown first
        st.dataframe(
            df_display,
            width="stretch",
            hide_index=True,
        )
        # st.markdown("#### Anomaly Score over Time")
        # df_plot = df.copy()
        # df_plot["timestamp"] = pd.to_datetime(df_plot["timestamp"])
        # df_plot = df_plot.set_index("timestamp")

        # st.line_chart(df_plot["anomaly_score"])
    else:
        st.info("No manual checks yet. Click btn on left for first data.")
st.markdown("---")
st.caption(
    "API health via `/status`, "
    "and model behaviour via manual probes to `/score` with a history of anomaly scores."
)
