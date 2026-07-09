from pathlib import Path
import hmac
import os
import shutil
import tempfile

import streamlit as st

from pcf_auto_review import run_review


st.set_page_config(page_title="PCF 自动复核", layout="wide")


def get_app_password():
    try:
        secret_password = st.secrets.get("APP_PASSWORD", "")
    except Exception:
        secret_password = ""
    return secret_password or os.environ.get("APP_PASSWORD", "")


def check_password():
    app_password = get_app_password()
    if not app_password:
        st.error("应用密码尚未配置。请在 Streamlit Secrets 或本地环境变量中设置 APP_PASSWORD。")
        st.stop()

    if st.session_state.get("password_ok"):
        return

    st.markdown("### 访问验证")
    st.caption("请输入访问密码后继续使用 PCF 自动复核工具。")
    password = st.text_input("访问密码", type="password")

    if password:
        if hmac.compare_digest(password, app_password):
            st.session_state["password_ok"] = True
            st.rerun()
        else:
            st.error("密码不正确，请重新输入。")
    st.stop()

st.markdown(
    """
    <style>
    :root {
        --pcf-ink: #17212b;
        --pcf-muted: #64727f;
        --pcf-line: #d8e1e8;
        --pcf-panel: #ffffff;
        --pcf-page: #f5f8fb;
        --pcf-teal: #0f766e;
        --pcf-teal-soft: #e6f4f1;
        --pcf-amber: #b7791f;
        --pcf-red: #b42318;
    }

    .stApp {
        background: var(--pcf-page);
        color: var(--pcf-ink);
        font-family: "Inter", "PingFang SC", "Microsoft YaHei", "Helvetica Neue", Arial, sans-serif;
    }

    [data-testid="stSidebar"] {
        background: #102230;
        color: #eef6f8;
        border-right: 1px solid #0b1923;
    }

    [data-testid="stSidebar"] * {
        color: #eef6f8;
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1220px;
    }

    h1, h2, h3 {
        letter-spacing: 0;
    }

    .pcf-hero {
        border: 1px solid var(--pcf-line);
        background: var(--pcf-panel);
        border-radius: 8px;
        padding: 26px 30px;
        margin-bottom: 18px;
        box-shadow: 0 18px 45px rgba(28, 47, 63, 0.08);
    }

    .pcf-eyebrow {
        display: inline-flex;
        align-items: center;
        padding: 5px 10px;
        border-radius: 999px;
        background: var(--pcf-teal-soft);
        color: var(--pcf-teal);
        font-size: 13px;
        font-weight: 700;
        margin-bottom: 12px;
    }

    .pcf-title {
        margin: 0;
        font-size: 32px;
        line-height: 1.25;
        font-weight: 760;
        color: var(--pcf-ink);
    }

    .pcf-subtitle {
        margin: 10px 0 0;
        color: var(--pcf-muted);
        font-size: 15px;
        line-height: 1.7;
        max-width: 760px;
    }

    .pcf-strip {
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 10px;
        margin-top: 20px;
    }

    .pcf-step {
        border: 1px solid var(--pcf-line);
        border-radius: 8px;
        padding: 12px 14px;
        background: #fbfdfe;
    }

    .pcf-step b {
        display: block;
        color: var(--pcf-ink);
        font-size: 14px;
        margin-bottom: 4px;
    }

    .pcf-step span {
        color: var(--pcf-muted);
        font-size: 13px;
    }

    .pcf-section-label {
        margin: 20px 0 8px;
        color: var(--pcf-ink);
        font-weight: 750;
        font-size: 17px;
    }

    .pcf-note {
        color: var(--pcf-muted);
        font-size: 13px;
        margin-top: -2px;
        margin-bottom: 12px;
    }

    div[data-testid="stFileUploader"] {
        background: #ffffff;
        border: 1px solid var(--pcf-line);
        border-radius: 8px;
        padding: 14px 16px 10px;
        box-shadow: 0 8px 24px rgba(28, 47, 63, 0.05);
    }

    div[data-testid="stFileUploader"] label {
        color: var(--pcf-ink);
        font-weight: 720;
    }

    div[data-testid="stFileUploaderDropzone"] {
        border: 1px dashed #aab8c4;
        background: #f9fbfd;
        border-radius: 8px;
    }

    .stButton > button, .stDownloadButton > button {
        border-radius: 8px;
        min-height: 46px;
        font-weight: 760;
        border: 1px solid #0d5f59;
    }

    .stButton > button[kind="primary"] {
        background: var(--pcf-teal);
        color: white;
    }

    [data-testid="stMetric"] {
        background: #ffffff;
        border: 1px solid var(--pcf-line);
        border-radius: 8px;
        padding: 14px 16px;
        box-shadow: 0 8px 24px rgba(28, 47, 63, 0.05);
    }

    [data-testid="stMetricLabel"] {
        color: var(--pcf-muted);
        font-weight: 700;
    }

    [data-testid="stMetricValue"] {
        color: var(--pcf-ink);
        font-weight: 780;
    }

    .pcf-success {
        border: 1px solid #a6d8cd;
        background: var(--pcf-teal-soft);
        color: #0b4f49;
        border-radius: 8px;
        padding: 14px 16px;
        font-weight: 650;
        margin: 12px 0;
    }

    @media (max-width: 800px) {
        .pcf-strip {
            grid-template-columns: 1fr;
        }
        .pcf-title {
            font-size: 26px;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

check_password()

st.markdown(
    """
    <div class="pcf-hero">
        <div class="pcf-eyebrow">ETF PCF Review Desk</div>
        <h1 class="pcf-title">PCF 自动复核</h1>
        <p class="pcf-subtitle">
            按日终复核顺序上传 T-1 估值数据、投资参数邮件和 PCF 清单文件，
            自动完成产品层、成份券层、估值字段、特殊设置和费率参数校验。
        </p>
        <div class="pcf-strip">
            <div class="pcf-step"><b>1. T-1 估值确认</b><span>校验 NAV、创设单位净值、现金差额。</span></div>
            <div class="pcf-step"><b>2. 投资参数维护</b><span>校验申赎单位、限额、替代比例和特殊券。</span></div>
            <div class="pcf-step"><b>3. PCF 清单复核</b><span>输出汇总、异常明细和完整复核留痕。</span></div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.header("复核步骤")
    st.write("1. 上传 T-1 估值数据")
    st.write("2. 上传投资邮件")
    st.write("3. 上传 PCF 文件夹中的 XML 与 flag/flg 文件")
    st.write("4. 点击开始复核并下载结果")
    st.divider()
    st.write("建议每次复核使用同一交易日批次文件，避免跨日文件混入。")

st.markdown('<div class="pcf-section-label">上传复核资料</div>', unsafe_allow_html=True)
st.markdown('<div class="pcf-note">上传顺序按日终业务链路排列：先估值数据，再投资参数，最后是系统生成的 PCF 清单。</div>', unsafe_allow_html=True)
col1, col2 = st.columns(2)
with col1:
    valuation_file = st.file_uploader("T-1日估值数据.xlsx", type=["xlsx"], key="valuation")
with col2:
    mail_file = st.file_uploader("投资邮件.xlsx", type=["xlsx"], key="mail")

pcf_files = st.file_uploader(
    "PCF 文件（可一次多选 XML、flag、flg）",
    type=["xml", "flag", "flg"],
    accept_multiple_files=True,
)

ready = bool(mail_file and valuation_file and pcf_files)

if not ready:
    st.info("请先上传三类资料。PCF 文件需要包含 XML 及对应 flag/flg 文件。")

run_clicked = st.button("开始复核", type="primary", disabled=not ready, use_container_width=True)

if run_clicked:
    with st.spinner("正在复核，请稍候..."):
        with tempfile.TemporaryDirectory(prefix="pcf_review_") as temp_root:
            temp_root = Path(temp_root)
            data_dir = temp_root / "datasets"
            pcf_dir = data_dir / "PCF"
            output_dir = temp_root / "output"
            pcf_dir.mkdir(parents=True, exist_ok=True)
            output_dir.mkdir(parents=True, exist_ok=True)

            (data_dir / "投资邮件.xlsx").write_bytes(mail_file.getbuffer())
            (data_dir / "T-1日估值数据.xlsx").write_bytes(valuation_file.getbuffer())
            for uploaded in pcf_files:
                (pcf_dir / Path(uploaded.name).name).write_bytes(uploaded.getbuffer())

            try:
                result = run_review(data_dir=data_dir, output_dir=output_dir)
            except Exception as exc:
                st.error("复核失败，请检查上传文件是否完整、文件名是否符合当日 PCF 命名规则。")
                st.exception(exc)
                st.stop()

            final_output = Path("output") / "PCF自动复核结果_界面版.xlsx"
            final_output.parent.mkdir(exist_ok=True)
            shutil.copy2(result["output_file"], final_output)

            summary = result["summary"].copy()
            module_summary = result["module_summary"].copy()
            exception_only = result["exception_only"].copy()
            output_bytes = final_output.read_bytes()

    pass_count = int((summary["复核结论"] == "通过").sum())
    fail_count = int((summary["复核结论"] == "不通过").sum())
    total_checks = int(result["checks"].shape[0])
    exception_count = int(exception_only.shape[0])

    st.markdown('<div class="pcf-section-label">复核结果</div>', unsafe_allow_html=True)
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("产品数", len(summary))
    m2.metric("通过", pass_count)
    m3.metric("不通过", fail_count)
    m4.metric("异常项", exception_count)

    if exception_only.empty:
        st.markdown('<div class="pcf-success">本次复核未发现异常，已生成完整复核底稿。</div>', unsafe_allow_html=True)

    st.download_button(
        "下载复核结果 Excel",
        data=output_bytes,
        file_name="PCF自动复核结果.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True,
    )

    tab_summary, tab_exception, tab_module = st.tabs(["汇总", "异常明细", "模块统计"])
    with tab_summary:
        st.dataframe(summary, use_container_width=True, hide_index=True)
    with tab_exception:
        if exception_only.empty:
            st.success("本次复核未发现异常。")
        else:
            st.dataframe(exception_only, use_container_width=True, hide_index=True)
    with tab_module:
        st.dataframe(module_summary, use_container_width=True, hide_index=True)

    st.caption(f"本次共完成 {total_checks} 项校验。")
