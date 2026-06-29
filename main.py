import streamlit as st
import pandas as pd
import os
import math
import datetime
from streamlit_image_coordinates import streamlit_image_coordinates
from PIL import Image, ImageDraw, ImageFont
import requests
import json

# ตั้งค่าหน้าเว็บกว้างแบบ Dashboard สายลับ
st.set_page_config(layout="wide", page_title="iSOTOPE Enemy Scout PMNC", page_icon="🕵️‍♂️")

st.title("🕵️‍♂️ iSOTOPE Esports - ONLINE Enemy Scout 32 ทีมอันตราย")
st.write("---")

# =========================================================================
# 🔗 [จุดสำคัญที่ 1] วางลิงก์ Google Sheets ของแคลนตรงนี้ (เอาไว้อ่านข้อมูลพล็อตจุด)
# =========================================================================
GOOGLE_SHEET_URL = "https://docs.google.com/spreadsheets/d/144NXorU4dmgcUa4we5tMtvLvLCDN9_DfrVSJovmGDhU/edit?gid=0#gid=0"

# =========================================================================
# 🔗 [จุดสำคัญที่ 2] วางลิงก์ Web App URL ที่ก๊อปมาจาก Apps Script ขั้นตอนที่ 1 ตรงนี้!
# =========================================================================
WEB_APP_URL = "https://script.google.com/macros/s/AKfycbwXK79K52JP3Q62ieeGF2n2Cn0c0JgZDSzdgfz0ycVeURFiotf-7URtKUWLQ_Hv3U-mvw/exec"


# ฟังก์ชันสำหรับแปลงลิงก์ดึงข้อมูลมาอ่าน
def get_csv_url(url):
    return url.replace("/edit?usp=sharing", "/gviz/tq?tqx=out:csv&sheet=ScoutData").replace("/edit", "/gviz/tq?tqx=out:csv&sheet=ScoutData")

# ฟังก์ชันดึงข้อมูลจาก Sheets มาพล็อตจุด
def load_online_data():
    try:
        csv_url = get_csv_url(GOOGLE_SHEET_URL)
        df = pd.read_csv(csv_url)
        if df.empty or "ทีมคู่แข่ง" not in df.columns:
            return pd.DataFrame(columns=["บันทึกเมื่อ", "ทัวร์นาเมนต์", "สัปดาห์", "แมตช์ที่", "ทีมคู่แข่ง", "แผนที่", "พฤติกรรม", "วงเฟสที่", "พิกัด_X", "พิกัด_Y", "บทวิเคราะห์จากโค้ช"])
        
        # ปรับชื่อคอลัมน์กูเกิลชีทให้ตรงกับระบบดึงข้อมูล
        df.columns = ["บันทึกเมื่อ", "ทัวร์นาเมนต์", "สัปดาห์", "แมตช์ที่", "ทีมคู่แข่ง", "แผนที่", "พฤติกรรม", "วงเฟสที่", "พิกัด_X", "พิกัด_Y", "บทวิเคราะห์จากโค้ช"]
        return df
    except Exception:
        return pd.DataFrame(columns=["บันทึกเมื่อ", "ทัวร์นาเมนต์", "สัปดาห์", "แมตช์ที่", "ทีมคู่แข่ง", "แผนที่", "พฤติกรรม", "วงเฟสที่", "พิกัด_X", "พิกัด_Y", "บทวิเคราะห์จากโค้ช"])

# โหลดข้อมูลล่าสุด
df_display = load_online_data()

map_images = {
    "Erangel": "erangel_map.webp",
    "Miramar": "miramar_map.webp",
    "Rondo": "rondo_map.webp"
}

ENEMY_COLOR = (255, 102, 0)
ENEMY_COLOR_RGBA = ENEMY_COLOR + (255,)
ENEMY_LINE_RGBA = ENEMY_COLOR + (160,)

def draw_arrow(draw, p1, p2, color, thickness=3):
    x1, y1 = p1
    x2, y2 = p2
    draw.line([p1, p2], fill=color, width=thickness)
    angle = math.atan2(y2 - y1, x2 - x1)
    arrow_length = 15
    arrow_p1 = (x2 - arrow_length * math.cos(angle - math.pi/6), y2 - arrow_length * math.sin(angle - math.pi/6))
    arrow_p2 = (x2 - arrow_length * math.cos(angle + math.pi/6), y2 - arrow_length * math.sin(angle + math.pi/6))
    draw.polygon([p2, arrow_p1, arrow_p2], fill=color)

tab1, tab2 = st.tabs(["📝 บันทึกพฤติกรรมทีมคู่แข่ง", "📊 แดชบอร์ดส่องจุดโดด/จุดมูฟศัตรู"])

# ==========================================
# แท็บที่ 1: บันทึกข้อมูลศัตรู
# ==========================================
with tab1:
    st.sidebar.header("📋 ข้อมูลทีมคู่แข่ง PMNC")
    enemy_team_name = st.sidebar.text_input("✍️ พิมพ์ชื่อทีมคู่แข่ง", "Team A").strip()
    tournament_name = st.sidebar.text_input("ชื่อทัวร์ / ลิงก์ห้องซ้อม", "PMNC Scrims", key="sc_tour")
    week_num = st.sidebar.selectbox("สัปดาห์ที่", ["Week 1", "Week 2", "Week 3", "Week 4"], key="sc_wk")
    match_num = st.sidebar.slider("แมตช์ที่", 1, 6, 1, key="sc_match")
    map_name = st.sidebar.selectbox("แผนที่", ["Erangel", "Miramar", "Rondo"], key="sc_map")
    
    event_type = st.sidebar.radio("พฤติกรรมที่ตรวจพบ", ["📌 Drop Zone", "🏃‍♂️ Move", "💀 จุดที่เขาปะทะ"], key="sc_event")
    circle_phase = st.sidebar.selectbox("เกิดขึ้นในวงเฟสไหน?", ["DZ", "P1", "P2", "P3", "P4", "P5", "P6", "P7", "P8"], key="sc_phase")
    coach_notes = st.sidebar.text_area("วิเคราะห์แผนเพิ่มเติม", "", key="sc_notes")

    st.subheader(f"🗺️ กำลังดักพิกัด: {event_type} ของทีม [{enemy_team_name}] บน {map_name}")

    if map_name in map_images and os.path.exists(map_images[map_name]):
        value = streamlit_image_coordinates(map_images[map_name], key=f"sc_click_{map_name}")
    else:
        st.warning("กรุณาตรวจสอบไฟล์รูปภาพแผนที่ในระบบ")
        value = None

    if value is not None:
        click_x = value["x"]
        click_y = value["y"]
        st.warning(f"📍 ล็อกเป้าหมายสำเร็จที่ X: {click_x}, Y: {click_y}")
        
        if st.button("💾 ยิงข้อมูลเข้าสารบบคลาวด์กลาง", type="primary"):
            current_timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # โครงสร้าง payload ส่งหาระบบชีทแบบเรียลไทม์
            payload = {
                "timestamp": current_timestamp,
                "tournament": tournament_name,
                "week": week_num,
                "match": match_num,
                "team": enemy_team_name,
                "map": map_name,
                "event": event_type,
                "phase": circle_phase,
                "x": click_x,
                "y": click_y,
                "notes": coach_notes
            }
            
            try:
                # ยิงคำสั่ง POST อัปเดตออนไลน์เข้ากูเกิลชีททันที
                response = requests.post(WEB_APP_URL, data=json.dumps(payload))
                if response.status_code == 200:
                    st.success(f"✅ บันทึกข้อมูลพิกัดทีม {enemy_team_name} เรียบร้อยแล้ว! ข้อมูลถูกซิงค์เข้า Google Sheets กลางเรียบร้อยครับ")
                    st.rerun()
                else:
                    st.error("❌ การเชื่อมต่อล้มเหลว แต่ข้อมูลบันทึกสำรองในแอปแล้ว")
            except Exception as e:
                st.error(f"เกิดข้อผิดพลาดในการส่งข้อมูล: {e}")
    else:
        st.write("👉 *กรุณาคลิกเลือกจุดบนแผนที่ก่อนกดบันทึกข้อมูล*")

# ==========================================
# แท็บที่ 2: แดชบอร์ดดึงข้อมูลออนไลน์มาพล็อตจุด
# ==========================================
with tab2:
    st.subheader("📈 แผงวิเคราะห์ยุทธวิธีออนไลน์ (ดึงข้อมูลเรียลไทม์)")
    
    if df_display.empty:
        st.info("🌐 ขณะนี้ยังไม่มีข้อมูลยุทธวิธีใน Google Sheets กลาง กรุณากรอกและส่งข้อมูลจากแท็บแรกครับ")
    else:
        col1, col2, col3 = st.columns(3)
        with col1:
            filter_map = st.selectbox("เลือกแผนที่ที่จะเปิดแกะรอย", ["Erangel", "Miramar", "Rondo"], key="fs_map")
        with col2:
            all_enemy_teams = ["ดูรวมทุกทีมศัตรู"] + list(df_display["ทีมคู่แข่ง"].dropna().unique())
            filter_enemy = st.selectbox("เลือกดูทีมคู่แข่ง", all_enemy_teams, key="fs_team")
        with col3:
            filter_event = st.selectbox("เลือกพฤติกรรมศัตรู", ["ทั้งหมด", "📌 Drop Zone", "🏃‍♂️ Move", "💀 จุดที่ปะทะ"], key="fs_event")
            
        df_filtered = df_display[df_display["แผนที่"] == filter_map]
        if filter_enemy != "ดูรวมทุกทีมศัตรู":
            df_filtered = df_filtered[df_filtered["ทีมคู่แข่ง"] == filter_enemy]
        if filter_event != "ทั้งหมด":
            df_filtered = df_filtered[df_filtered["พฤติกรรม"].str.strip() == filter_event.strip()]
            
        st.write(f"📊 ตรวจพบข้อมูลยุทธวิธีตรงตามเงื่อนไข ทั้งหมด **{len(df_filtered)}** พิกัด")
        
        if filter_map in map_images and os.path.exists(map_images[filter_map]):
            img_target_path = map_images[filter_map]
            base_image = Image.open(img_target_path).convert("RGBA")
            overlay = Image.new("RGBA", base_image.size, (0, 0, 0, 0))
            draw_overlay = ImageDraw.Draw(overlay)
            draw_base = ImageDraw.Draw(base_image)
            
            font = ImageFont.load_default()

            # --- วาดเส้น Move ---
            df_move_only = df_display[(df_display["แผนที่"] == filter_map) & (df_display["พฤติกรรม"].str.contains("Move", na=False))]
            enemies_to_draw = list(df_move_only["ทีมคู่แข่ง"].unique()) if filter_enemy == "ดูรวมทุกทีมศัตรู" else [filter_enemy]
            
            for current_e in enemies_to_draw:
                df_enemy_move = df_move_only[df_move_only["ทีมคู่แข่ง"] == current_e]
                for (tour, m_id), sub_df in df_enemy_move.groupby(["ทัวร์นาเมนต์", "แมตช์ที่"]):
                    if "บันทึกเมื่อ" in sub_df.columns and not sub_df["บันทึกเมื่อ"].isna().all():
                        sub_df = sub_df.sort_values("บันทึกเมื่อ")
                    if len(sub_df) > 1:
                        points = list(zip(sub_df["พิกัด_X"], sub_df["พิกัด_Y"]))
                        for i in range(len(points) - 1):
                            draw_arrow(draw_base, points[i], points[i+1], color=ENEMY_LINE_RGBA, thickness=3)

            # --- วาดจุดสัญลักษณ์และชื่อ ---
            for index, row in df_filtered.iterrows():
                try:
                    x = float(row["พิกัด_X"])
                    y = float(row["พิกัด_Y"])
                except:
                    continue
                enemy_name = row["ทีมคู่แข่ง"]
                p_type = str(row["พฤติกรรม"]).strip()
                phase_info = row["วงเฟสที่"]
                m_info = row["แมตช์ที่"]
                
                if "Drop Zone" in p_type:
                    r = 12  
                    draw_base.ellipse([x - r, y - r, x + r, y + r], outline=ENEMY_COLOR_RGBA, width=5)
                elif "Move" in p_type:
                    r = 9
                    draw_base.ellipse([x - r, y - r, x + r, y + r], fill=ENEMY_COLOR_RGBA, outline=(255, 255, 255), width=2)
                else:
                    size = 12
                    draw_base.line([(x - size, y - size), (x + size, y + size)], fill=ENEMY_COLOR_RGBA, width=5)
                    draw_base.line([(x - size, y + size), (x + size, y - size)], fill=ENEMY_COLOR_RGBA, width=5)
                
                offset_y = 28  
                text_content = f" [{enemy_name}] (M{m_info} | {phase_info}) "
                
                if hasattr(draw_base, "textbbox"):
                    bbox = draw_base.textbbox((0, 0), text_content, font=font)
                    text_w = bbox[2] - bbox[0]
                    text_h = bbox[3] - bbox[1]
                else:
                    text_w = len(text_content) * 6
                    text_h = 10
                
                box_x1 = x - (text_w / 2)
                box_y1 = y + offset_y
                box_x2 = x + (text_w / 2)
                box_y2 = box_y1 + text_h + 6
                
                draw_overlay.rectangle([box_x1, box_y1, box_x2, box_y2], fill=(0, 0, 0, 180))
                draw_overlay.text((box_x1, box_y1 + 3), text_content, fill=(255, 255, 255, 255), font=font)
                
            final_image = Image.alpha_composite(base_image, overlay).convert("RGB")
            st.image(final_image, caption=f"🛰️ แผงวิเคราะห์ยุทธวิธีแคลน iSOTOPE แผนที่: {filter_map}", use_container_width=True)
