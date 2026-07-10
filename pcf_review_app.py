from pathlib import Path
import hmac
import os
import shutil
import tempfile

import streamlit as st

from pcf_auto_review import run_review


st.set_page_config(page_title="ETF PCF 自动复核系统", layout="wide")


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

    .pcf-upload-status {
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 10px;
        margin: 12px 0 16px;
    }

    .pcf-status-item {
        border: 1px solid var(--pcf-line);
        border-radius: 8px;
        background: #ffffff;
        padding: 10px 12px;
        color: var(--pcf-muted);
        font-size: 13px;
        font-weight: 650;
    }

    .pcf-status-item.ready {
        border-color: #a6d8cd;
        background: var(--pcf-teal-soft);
        color: #0b4f49;
    }

    .pcf-output-list {
        border: 1px solid var(--pcf-line);
        background: #ffffff;
        border-radius: 8px;
        padding: 14px 18px;
        margin: 12px 0 14px;
    }

    .pcf-output-list p {
        margin: 0 0 8px;
        color: var(--pcf-ink);
        font-weight: 720;
    }

    .pcf-output-list ol {
        margin: 0;
        padding-left: 22px;
        color: var(--pcf-muted);
        line-height: 1.8;
        font-size: 14px;
    }

    @media (max-width: 800px) {
        .pcf-strip {
            grid-template-columns: 1fr;
        }
        .pcf-upload-status {
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
        <h1 class="pcf-title">ETF申购赎回清单（PCF）自动复核系统</h1>
        <p class="pcf-subtitle">
            请按照ETF日终PCF复核流程依次上传T-1估值数据、投资参数文件及系统生成的PCF清单文件，
            系统将自动完成产品信息、成份券配置、估值信息及申赎业务参数的一致性校验，并生成复核结果。
        </p>
        <div class="pcf-strip">
            <div class="pcf-step"><b>1. T-1 估值确认</b><span>校验 NAV、创设单位净值、现金差额。</span></div>
            <div class="pcf-step"><b>2. 投资参数维护</b><span>校验申赎单位、限额、替代比例和特殊成份券。</span></div>
            <div class="pcf-step"><b>3. PCF 清单复核</b><span>输出汇总、异常明细和完整复核留痕。</span></div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.header("复核步骤")
    st.write("1. 上传T-1估值数据文件")
    st.write("2. 上传投资参数文件")
    st.write("3. 上传PCF清单文件（XML及对应辅助文件）")
    st.write("4. 执行自动复核并下载复核结果")
    st.divider()
    st.write("建议每次复核使用同一交易日批次文件，避免跨日文件混入。")

st.markdown('<div class="pcf-section-label">PCF复核资料上传</div>', unsafe_allow_html=True)
st.markdown('<div class="pcf-note">请按照日终PCF复核流程依次上传以下资料：T-1估值数据、投资参数文件及PCF清单文件。</div>', unsafe_allow_html=True)
col1, col2 = st.columns(2)
with col1:
    valuation_file = st.file_uploader("T-1估值数据文件.xlsx", type=["xlsx"], key="valuation")
    st.caption("用于校验PCF生成所依据的NAV、单位净值及现金差额等估值信息。")
with col2:
    mail_file = st.file_uploader("投资参数文件.xlsx", type=["xlsx"], key="mail")
    st.caption("包含ETF申赎参数及特殊成份券配置，用于校验业务规则及参数设置。")

pcf_files = st.file_uploader(
    "PCF清单文件（XML及辅助文件）",
    type=["xml", "flag", "flg"],
    accept_multiple_files=True,
)
st.caption("支持同时上传XML文件及对应flag/flg辅助文件。")

ready = bool(mail_file and valuation_file and pcf_files)

valuation_status = "ready" if valuation_file else ""
mail_status = "ready" if mail_file else ""
pcf_status = "ready" if pcf_files else ""
valuation_text = "✓ T-1估值数据已上传" if valuation_file else "T-1估值数据待上传"
mail_text = "✓ 投资参数文件已上传" if mail_file else "投资参数文件待上传"
pcf_text = "✓ PCF清单文件已上传" if pcf_files else "PCF清单文件待上传"
st.markdown(
    f"""
    <div class="pcf-upload-status">
        <div class="pcf-status-item {valuation_status}">{valuation_text}</div>
        <div class="pcf-status-item {mail_status}">{mail_text}</div>
        <div class="pcf-status-item {pcf_status}">{pcf_text}</div>
    </div>
    """,
    unsafe_allow_html=True,
)

if not ready:
    st.info("请完成T-1估值数据、投资参数文件及PCF清单文件上传后开始自动复核。PCF清单文件需包含XML及对应辅助文件。")

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

    st.markdown(
        """
        <div class="pcf-output-list">
            <p>复核完成，已生成以下结果文件：</p>
            <ol>
                <li>复核结果汇总表</li>
                <li>异常明细清单</li>
                <li>复核底稿</li>
            </ol>
        </div>
        """,
        unsafe_allow_html=True,
    )

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
