import streamlit as st
import streamlit.components.v1 as components
import json

# Page setup
st.set_page_config(page_title="VSC & Shrink Factor Tool", page_icon="⚙️", layout="centered")

# Forcefully disable browser autofill/history popup on all inputs
components.html("""
<script>
function disableAutofill() {
    const inputs = window.parent.document.querySelectorAll('input');
    inputs.forEach((input, idx) => {
        input.setAttribute('autocomplete', 'new-password');
        input.setAttribute('autocorrect', 'off');
        input.setAttribute('autocapitalize', 'off');
        input.setAttribute('spellcheck', 'false');
        if (!input.dataset.randName) {
            input.setAttribute('name', 'field_' + Math.random().toString(36).substring(2) + '_' + idx);
            input.dataset.randName = 'true';
        }
    });
}
disableAutofill();
const observer = new MutationObserver(disableAutofill);
observer.observe(window.parent.document.body, { childList: true, subtree: true });
</script>
""", height=0)

def render_blue_copy_box(label, value, is_mono=False):
    val_str = str(value)
    js_val = json.dumps(val_str)
    font_style = "font-family: monospace; font-size: 18px;" if is_mono else "font-family: sans-serif; font-size: 24px;"
    
    html_code = f"""
    <div style="
        background-color: #1E88E5;
        color: white;
        padding: 14px 18px;
        border-radius: 10px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-family: sans-serif;
        box-shadow: 0 2px 6px rgba(0,0,0,0.12);
    ">
        <div style="overflow-x: auto; padding-right: 10px;">
            <div style="font-size: 13px; opacity: 0.9; margin-bottom: 4px;">{label}</div>
            <div style="{font_style} font-weight: 700; white-space: nowrap;">{val_str}</div>
        </div>
        <button id="copyBtn" onclick="copyText()" style="
            background-color: rgba(255, 255, 255, 0.2);
            color: white;
            border: 1px solid rgba(255, 255, 255, 0.5);
            border-radius: 6px;
            padding: 6px 12px;
            cursor: pointer;
            font-size: 13px;
            font-weight: 600;
            white-space: nowrap;
        ">📋 Copy</button>
    </div>
    <script>
    function copyText() {{
        const text = {js_val};
        navigator.clipboard.writeText(text).then(function() {{
            const btn = document.getElementById('copyBtn');
            btn.innerText = '✅ Copied!';
            btn.style.backgroundColor = '#2E7D32';
            setTimeout(() => {{
                btn.innerText = '📋 Copy';
                btn.style.backgroundColor = 'rgba(255, 255, 255, 0.2)';
            }}, 1500);
        }});
    }}
    </script>
    """
    components.html(html_code, height=92)

# Accept only '$' or plain numeric value (rejects commas or other symbols)
def parse_number(val_str):
    cleaned = val_str.strip()
    if cleaned == "":
        return None
    if cleaned.startswith("$"):
        cleaned = cleaned[1:].strip()
    if cleaned == "":
        raise ValueError("Empty value after $")
    return float(cleaned)

st.title("⚙️ VSC & Shrink Factor Calculator")
st.write("Enter the inputs below to generate results automatically.")

st.divider()

# 1. Shrink Factor & ABC Code Inputs
st.subheader("1. Shrink Factor & ABC Code")
st.caption("Shrink Factor – This is for SMT parts. | ABC Code (this is based on the item cost)")

is_smt = st.checkbox("Is this an SMT part?", value=True)
val_input = st.text_input("Enter Item Cost (e.g., 0.36, 25, or $25):", value="", key="val_field")

# Formula 1: Applies only if SMT part is checked; otherwise 0
def get_shrink_factor(val_str, smt_flag):
    try:
        num = parse_number(val_str)
        if num is None:
            return "-"
        if not smt_flag:
            return 0
        if num == 0:
            return 0
        elif num <= 1:
            return 0.01
        elif num <= 2:
            return 0.02
        else:
            return 0
    except ValueError:
        return "Invalid Input"

# Formula 2: =IF(A1="", "", IF(A1>25, "A", IF(A1>=5, "B", "C")))
def get_abc_code(val_str):
    try:
        num = parse_number(val_str)
        if num is None:
            return "-"
        if num > 25:
            return "A"
        elif num >= 5:
            return "B"
        else:
            return "C"
    except ValueError:
        return "Invalid Input"

sf_result = get_shrink_factor(val_input, is_smt)
abc_result = get_abc_code(val_input)

col1, col2 = st.columns(2)
with col1:
    render_blue_copy_box("Shrink Factor – This is for SMT parts.", sf_result)

with col2:
    render_blue_copy_box("ABC Code (this is based on the item cost)", abc_result)

st.divider()

# 2. VSC Document Link Generator
st.subheader("2. VSC Document Link")
part_input = st.text_input("Enter VSC Item / Part Number (e.g., 4840-631):", value="", key="part_field")

# Formula 3: ="\parts\" & LEFT(E1, FIND("-", E1)-1) & "\" & E1
def get_vsc_path(part_str):
    part_str = part_str.strip()
    if part_str == "":
        return ""
    if "-" in part_str:
        prefix = part_str.split("-")[0]
        return rf"\parts\{prefix}\{part_str}"
    else:
        return "Error: Missing '-' hyphen"

vsc_link = get_vsc_path(part_input)

if vsc_link:
    render_blue_copy_box("Generated Path", vsc_link, is_mono=True)
