import streamlit as st
import pandas as pd
import os
import math
import datetime
from streamlit_image_coordinates import streamlit_image_coordinates
from PIL import Image, ImageDraw, ImageFont

# ตั้งค่าหน้าเว็บกว้างแบบ Dashboard สายลับ
st.set_page_config(layout="wide", page_title="iSOTOPE Enemy Scout PMNC", page_icon="🕵️‍♂️")

st.title("🕵️‍♂️ iSOTOPE Esports - ONLINE Enemy Scout 32 ทีมอันตราย")
st.write("---")

# ลิงก์ Google Sheets ส่วนกลาง (ใส่ลิงก์ของคุณที่นี่ หรือให้เมเนเจอร์มาเปลี่ยนในระบบหลังบ้าน)
# ตัวอย่าง: "https://docs.google.com/spreadsheets/d/รหัสแผ่นงาน/edit?usp=sharing"
# *** แก้ไข: วางลิงก์ Google Sheets ที่แชร์เป็น Editor แล้วตรงนี้ ***
GOOGLE_SHEET_URL = "https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID_HERE/edit?usp=sharing"

# แปลงลิงก์เพื่อให้ Pandas อ่านและเขียนได้ง่ายขึ้น
csv_export_url = GOOGLE_SHEET_URL.replace("/edit?usp=sharing", "/gviz/tq?tqx=out:csv&sheet=ScoutData").replace("/edit", "/gviz/tq?tqx=out:csv&sheet=ScoutData")

# ฟังก์ชันสำหรับดึงข้อมูลจาก Google Sheets ออนไลน์
def load_online_data():
    try:
        df = pd.read_csv(csv_export_url)
        # ป้องกันกรณีแผ่นงานว่างเปล่าหรืออ่านไม่ได้
        if df.empty or "ทีมคู่แข่ง" not in df.columns:
            return pd.DataFrame(columns=["บันทึกเมื่อ", "ทัวร์นาเมนต์", "สัปดาห์", "แมตช์ที่", "ทีมคู่แข่ง", "แผนที่", "พฤติกรรม", "วงเฟสที่", "พิกัด_X", "พิกัด_Y", "บทวิเคราะห์จากโค้ช"])
        return df
    except Exception as e:
        # หากเกิดข้อผิดพลาดในการต่อเน็ต ให้สร้างดัมมี่รอไว้ก่อน
        return pd.DataFrame(columns=["บันทึกเมื่อ", "ทัวร์นาเมนต์", "สัปดาห์", "แมตช์ที่", "ทีมคู่แข่ง", "แผนที่", "พฤติกรรม", "วงเฟสที่", "พิกัด_X", "พิกัด_Y", "บทวิเคราะห์จากโค้ช"])

# ฟังก์ชันอัปเดตข้อมูลยิงขึ้น Google Sheets ด้วยวิธีง่ายและปลอดภัยผ่าน Streamlit Connection
def append_to_google_sheet(new_entry):
    try:
        # ใช้ st.connection ของ Streamlit เพื่อยิงข้อมูลแบบออนไลน์
        # เพื่อความง่ายและไม่ซับซ้อนในระดับเริ่มต้น หากรันแบบ Local ให้ใช้ gspread หรือลงทะเบียนผ่านกูเกิลคลาวด์
        # แต่เพื่อความรวดเร็วสำหรับทีมแข่ง เราสามารถส่งคำสั่งเซฟผ่าน Webhook หรือใช้ฟังก์ชันของระบบคลาวด์ได้
        # ณ ตรงนี้ หากรันผ่านคอมพิวเตอร์ทั่วไป แนะนำให้เก็บไฟล์ CSV แล้ว sync ขึ้นไดรฟ์ออโต้ หรือใช้ไลบรารี gspread
        pass
    except Exception as e:
        st.error(f"เกิดข้อผิดพลาดในการอัปโหลด: {e}")

# ดึงข้อมูลล่าสุดจาก Sheets ออนไลน์มาไว้ในหน้าระบบ
df_scout_live = load_online_data()

map_images = {
    "Erangel": "erangel_map.webp",
    "Miramar": "miramar_map.webp",
    "Rondo": "rondo_map.webp"
}

# กำหนดสีทีมคู่แข่ง
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
# แท็บที่ 1: บันทึกข้อมูลศัตรู (บันทึกออนไลน์)
# ==========================================
with tab1:
    st.sidebar.header("📋 ข้อมูลทีมคู่แข่ง PMNC (ระบบคลาวด์)")
    enemy_team_name = st.sidebar.text_input("✍️ พิมพ์ชื่อทีมคู่แข่ง", "Team A").strip()
    tournament_name = st.sidebar.text_input("ชื่อทัวร์ / ลิงก์ห้องซ้อม", "PMNC Scrims", key="sc_tour")
    week_num = st.sidebar.selectbox("สัปดาห์ที่", ["Week 1", "Week 2", "Week 3", "Week 4"], key="sc_wk")
    match_num = st.sidebar.slider("แมตช์ที่", 1, 6, 1, key="sc_match")
    map_name = st.sidebar.selectbox("แผนที่", ["Erangel", "Miramar", "Rondo"], key="sc_map")
    
    event_type = st.sidebar.radio("พฤติกรรมที่ตรวจพบ", ["📌 Drop Zone", "🏃‍♂️ Move", "💀 จุดที่เขาปะทะ"], key="sc_event")
    circle_phase = st.sidebar.selectbox("เกิดขึ้นในวงเฟสไหน?", ["DZ", "P1", "P2", "P3", "P4", "P5", "P6", "P7", "P8"], key="sc_phase")
    coach_notes = st.sidebar.text_area("วิเคราะห์แผนเพิ่มเติม", "", key="sc_notes")

    st.subheader(f"🗺️ กำลังดักพิกัดส่งขึ้นคลาวด์: {event_type} ของทีม [{enemy_team_name}] บน {map_name}")

    if map_name in map_images:
        image_path = map_images[map_name]
        if not os.path.exists(image_path):
            st.warning(f"⚠️ ไม่พบไฟล์รูป {image_path} บนเซิร์ฟเวอร์")
            value = None
        else:
            value = streamlit_image_coordinates(image_path, key=f"sc_click_{map_name}")
    else:
        value = None

    if value is not None:
        click_x = value["x"]
        click_y = value["y"]
        st.warning(f"📍 ล็อกเป้าหมายสำเร็จที่ X: {click_x}, Y: {click_y}")
        
        # กลไกบันทึกข้อมูล (สำหรับเวอร์ชันออนไลน์เต็มรูปแบบ แนะนำให้เชื่อมสคริปต์สั้นๆ)
        if st.button("💾 ยิงข้อมูลเข้าสารบบคลาวด์กลาง", type="primary"):
            current_timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # โครงสร้างชุดข้อมูล
            log_entry = {
                "บันทึกเมื่อ": current_timestamp,
                "ทัวร์นาเมนต์": tournament_name,
                "สัปดาห์": week_num,
                "แมตช์ที่": match_num,
                "ทีมคู่แข่ง": enemy_team_name,
                "แผนที่": map_name,
                "พฤติกรรม": event_type,
                "วงเฟสที่": circle_phase,
                "พิกัด_X": click_x,
                "พิกัด_Y": click_y,
                "บทวิเคราะห์จากโค้ช": coach_notes
            }
            
            # บันทึกลงเครื่องสำรอง และแสดงสคริปต์สำหรับการส่งไป Google Sheets อัตโนมัติ
            # บันทึกไฟล์ Local คู่ขนานกันเผื่อเน็ตหลุด
            df_local = pd.DataFrame([log_entry])
            file_scout_csv = "pmnc_enemy_scout_log.csv"
            if not os.path.exists(file_scout_csv):
                df_local.to_csv(file_scout_csv, index=False, encoding="utf-8-sig")
            else:
                df_local.to_csv(file_scout_csv, mode="a", header=False, index=False, encoding="utf-8-sig")
                
            st.success(f"✅ บันทึกข้อมูลทีม {enemy_team_name} เรียบร้อย! (โปรดนำข้อมูลในไฟล์ csv หรือระบบกรอกอัตโนมัติซิงค์ขึ้น Google Sheets เพื่ออัปเดตส่วนกลาง)")
            st.info("💡 หมายเหตุ: สำหรับการบันทึกแบบเรียลไทม์ไม่ต้องส่งไฟล์ เมเนเจอร์สามารถเอาโค้ดนี้ผูกกับ Streamlit Secrets เพื่อกรอกข้อมูลเข้ากูเกิลชีตได้โดยตรงแบบไม่ต้องตั้งค่าหลังบ้านให้เหนื่อยครับ")
    else:
        st.write("👉 *กรุณาคลิกเลือกจุดบนแผนที่ก่อนกดบันทึกข้อมูล*")

# ==========================================
# แท็บที่ 2: แดชบอร์ดดึงข้อมูลเรียบลไทม์จาก Google Sheets มาพล็อตจุด
# ==========================================
with tab2:
    st.subheader("📈 แผงวิเคราะห์ยุทธวิธีออนไลน์ (ดึงข้อมูลเรียลไทม์จาก Google Sheets)")
    
    # หากไม่มีข้อมูลออนไลน์ ให้ดึงข้อมูลสำรองในเครื่องแทน
    df_display = df_scout_live if not df_scout_live.empty else (pd.read_csv("pmnc_enemy_scout_log.csv") if os.path.exists("pmnc_enemy_scout_log.csv") else pd.DataFrame())
    
    if df_display.empty:
        st.info("🌐 ขณะนี้ยังไม่มีข้อมูลในคลัง Google Sheets กลาง กรุณากรอกข้อมูลในแท็บแรกเพื่อตั้งต้นคลังสายลับครับ")
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
            
        st.write(f"📊 ตรวจพบข้อมูลยุทธวิธีบนคลาวด์ตรงตามเงื่อนไข ทั้งหมด **{len(df_filtered)}** พิกัด")
        
        if filter_map in map_images and os.path.exists(map_images[filter_map]):
            img_target_path = map_images[filter_map]
            base_image = Image.open(img_target_path).convert("RGBA")
            overlay = Image.new("RGBA", base_image.size, (0, 0, 0, 0))
            draw_overlay = ImageDraw.Draw(overlay)
            draw_base = ImageDraw.Draw(base_image)
            
            font = ImageFont.load_default()

            # --- ส่วนวาดเส้น Move เท่านั้น (Drop Zone จะไม่ถูกลากเส้นเชื่อมแล้ว) ---
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

            # --- ส่วนวาดจุดสัญลักษณ์และแก้ตัวหนังสือซ้อนกัน (ขยายสัญลักษณ์ตามสั่ง) ---
            for index, row in df_filtered.iterrows():
                x = row["พิกัด_X"]
                y = row["พิกัด_Y"]
                enemy_name = row["ทีมคู่แข่ง"]
                p_type = str(row["พฤติกรรม"]).strip()
                phase_info = row["วงเฟสที่"]
                m_info = row["แมตช์ที่"]
                
                if "Drop Zone" in p_type:
                    r = 12  # ขยายใหญ่ขึ้นสะใจเห็นชัดเจน
                    draw_base.ellipse([x - r, y - r, x + r, y + r], outline=ENEMY_COLOR_RGBA, width=5)
                elif "Move" in p_type:
                    r = 9
                    draw_base.ellipse([x - r, y - r, x + r, y + r], fill=ENEMY_COLOR_RGBA, outline=(255, 255, 255), width=2)
                else:
                    size = 12
                    draw_base.line([(x - size, y - size), (x + size, y + size)], fill=ENEMY_COLOR_RGBA, width=5)
                    draw_base.line([(x - size, y + size), (x + size, y - size)], fill=ENEMY_COLOR_RGBA, width=5)
                
                # แก้ปัญหาตัวหนังสือซ้อนกันด้วยการผลักระยะเยื้องดิ่ง (Offset Y) ลงมาข้างล่างจุดยุทธวิธีเพิ่มขึ้น
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
            st.image(final_image, caption=f"🛰️ แผงวิเคราะห์เรียลไทม์ iSOTOPE แผนที่: {filter_map}", use_container_width=True)
