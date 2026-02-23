import flet as ft
import socket
import math
from datetime import datetime, timezone
import time
import json
import os
import threading
import traceback
import asyncio
from dotenv import load_dotenv
import os


# ===========================
# 1. 天文算法引擎
# ===========================
OBSERVER_LAT = 22.3
OBSERVER_LON = 114.1


def update_location_from_network():
    global OBSERVER_LAT, OBSERVER_LON
    try:
        import requests
        response = requests.get("https://ipapi.co/json/", timeout=5).json()
        lat = response.get("latitude")
        lon = response.get("longitude")
        if lat is not None and lon is not None:
            OBSERVER_LAT = lat
            OBSERVER_LON = lon
            print(f"位置已自动更新: {OBSERVER_LAT}, {OBSERVER_LON}")
    except Exception as e:
        print(f"联网获取位置失败，使用默认坐标: {e}")


def get_julian_date():
    now = datetime.now(timezone.utc)
    y, m = now.year, now.month
    d = now.day + now.hour / 24.0 + now.minute / 1440.0 + now.second / 86400.0
    if m <= 2:
        y -= 1
        m += 12
    A = math.floor(y / 100)
    B = 2 - A + math.floor(A / 4)
    return math.floor(365.25 * (y + 4716)) + math.floor(30.6001 * (m + 1)) + d + B - 1524.5


def get_real_planet_coords(body):
    D = get_julian_date() - 2451545.0
    obl = math.radians(23.4393 - 3.563e-7 * D)
    try:
        if body == 'Sun':
            w = 282.9404 + 4.70935e-5 * D
            e = 0.016709 - 1.151e-9 * D
            M = (356.0470 + 0.9856002585 * D) % 360.0
            M_rad = math.radians(M)
            E = M_rad + e * math.sin(M_rad) * (1.0 + e * math.cos(M_rad))
            x = math.cos(E) - e
            y = math.sin(E) * math.sqrt(1 - e * e)
            v = math.degrees(math.atan2(y, x))
            lon_rad = math.radians((v + w) % 360.0)
            x_equat = math.cos(lon_rad)
            y_equat = math.sin(lon_rad) * math.cos(obl)
            z_equat = math.sin(lon_rad) * math.sin(obl)
            ra = math.degrees(math.atan2(y_equat, x_equat)) % 360.0
            dec = math.degrees(math.asin(z_equat))
            return ra, dec

        elif body == 'Moon':
            L = (218.316 + 13.176396 * D) % 360.0
            M = (134.963 + 13.064993 * D) % 360.0
            F = (93.272 + 13.229350 * D) % 360.0
            lon = L + 6.289 * math.sin(math.radians(M))
            lat = 5.128 * math.sin(math.radians(F))
            lon_rad, lat_rad = math.radians(lon), math.radians(lat)
            x = math.cos(lon_rad) * math.cos(lat_rad)
            y = math.sin(lon_rad) * math.cos(lat_rad)
            z = math.sin(lat_rad)
            x_equat = x
            y_equat = y * math.cos(obl) - z * math.sin(obl)
            z_equat = y * math.sin(obl) + z * math.cos(obl)
            ra = math.degrees(math.atan2(y_equat, x_equat)) % 360.0
            dec = math.degrees(math.asin(z_equat))
            return ra, dec

        elif body == 'Mars':
            w_m = 286.5016 + 2.92961e-5 * D
            e_m = 0.093405 + 2.516e-9 * D
            M_m = (19.3871 + 0.52402073 * D) % 360.0
            a_m = 1.523688
            i_m = math.radians(1.8496 - 8.131e-6 * D)
            node_m = math.radians(49.5581 + 2.11081e-5 * D)
            M_rad = math.radians(M_m)
            E_rad = M_rad + e_m * \
                math.sin(M_rad) * (1.0 + e_m * math.cos(M_rad))
            xv = a_m * (math.cos(E_rad) - e_m)
            yv = a_m * (math.sqrt(1 - e_m * e_m) * math.sin(E_rad))
            v_m = math.atan2(yv, xv)
            r_m = math.sqrt(xv * xv + yv * yv)
            w_rad = math.radians(w_m)
            xh = r_m * (math.cos(node_m) * math.cos(v_m + w_rad - node_m) -
                        math.sin(node_m) * math.sin(v_m + w_rad - node_m) * math.cos(i_m))
            yh = r_m * (math.sin(node_m) * math.cos(v_m + w_rad - node_m) +
                        math.cos(node_m) * math.sin(v_m + w_rad - node_m) * math.cos(i_m))
            zh = r_m * (math.sin(v_m + w_rad - node_m) * math.sin(i_m))
            w_s = 282.9404 + 4.70935e-5 * D
            M_s_rad = math.radians((356.0470 + 0.9856002585 * D) % 360.0)
            E_s_rad = M_s_rad + 0.016709 * math.sin(M_s_rad)
            xv_s = math.cos(E_s_rad) - 0.016709
            yv_s = math.sin(E_s_rad) * math.sqrt(1 - 0.016709 ** 2)
            lon_s = math.atan2(yv_s, xv_s) + math.radians(w_s)
            r_s = math.sqrt(xv_s ** 2 + yv_s ** 2)
            xs, ys = r_s * math.cos(lon_s), r_s * math.sin(lon_s)
            xg, yg, zg = xh + xs, yh + ys, zh
            x_equat = xg
            y_equat = yg * math.cos(obl) - zg * math.sin(obl)
            z_equat = yg * math.sin(obl) + zg * math.cos(obl)
            ra = math.degrees(math.atan2(y_equat, x_equat)) % 360.0
            dist = math.sqrt(x_equat ** 2 + y_equat ** 2 + z_equat ** 2)
            dec = math.degrees(math.asin(z_equat / dist))
            return ra, dec
    except Exception as e:
        print(f"Math Error: {e}")
    return 0, 0


def get_az_alt(ra_deg, dec_deg):
    try:
        JD = get_julian_date()
        GMST = (18.697374558 + 24.06570982441908 * (JD - 2451545.0)) % 24
        LST_deg = (GMST * 15 + OBSERVER_LON) % 360
        RA_deg = float(ra_deg)
        Dec_rad = math.radians(float(dec_deg))
        Lat_rad = math.radians(OBSERVER_LAT)
        HA_rad = math.radians(LST_deg - RA_deg)
        sin_Alt = (math.sin(Dec_rad) * math.sin(Lat_rad) +
                   math.cos(Dec_rad) * math.cos(Lat_rad) * math.cos(HA_rad))
        Alt_rad = math.asin(sin_Alt)
        y_az = -math.sin(HA_rad)
        x_az = (math.cos(Lat_rad) * math.tan(Dec_rad) -
                math.sin(Lat_rad) * math.cos(HA_rad))
        Az_rad = math.atan2(y_az, x_az)
        return (math.degrees(Az_rad) % 360), math.degrees(Alt_rad)
    except Exception as e:
        print(f"AzAlt Error: {e}")
        return 0, 0


def get_star_coords(name):
    ra, dec = get_real_planet_coords(name)
    az, alt = get_az_alt(ra, dec)
    return ra, dec, az, alt


def send_udp_command(ip, ra_str, dec_str):
    try:
        ra_val = float(str(ra_str).replace('°', '').strip())
        dec_val = float(str(dec_str).replace('°', '').strip())
        cmd = f"{ra_val:.4f},{dec_val:.4f}"
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(1.5)
        sock.sendto(cmd.encode('utf-8'), (ip, 8888))
        sock.close()
        return True, f"Success: {ra_val:.2f}, {dec_val:.2f}"
    except Exception as e:
        return False, f"UDP Error: {e}"


# ===========================
# 2. AI 识别逻辑 (Astrometry API)
# ===========================

load_dotenv()  # 加载 .env 文件
MY_API_KEY = os.getenv("ASTROMETRY_API_KEY", "如果没有读到就用备用字符")


def solve_star_image(file_path=None, file_bytes=None, progress_cb=None):
    """
    识别星图。支持 file_path 或 file_bytes（Android 可能只有 bytes）。
    progress_cb(msg) 可选回调，用于更新 UI 进度。
    """
    import requests as req

    def _report(msg):
        if progress_cb:
            try:
                progress_cb(msg)
            except Exception:
                pass

    # 准备文件数据
    if file_bytes:
        pass  # 直接用 bytes
    elif file_path and os.path.exists(file_path):
        with open(file_path, 'rb') as f:
            file_bytes = f.read()
    else:
        return False, 0, 0, 0, 0, f"文件不存在: {file_path}"

    try:
        _report("🔗 连接 Astrometry.net ...")
        login_url = 'https://nova.astrometry.net/api/login'
        res = req.post(login_url, data={
            'request-json': json.dumps({"apikey": MY_API_KEY})
        }, timeout=15)
        session = res.json().get('session')
        if not session:
            return False, 0, 0, 0, 0, "Astrometry 登录失败"

        _report("📤 上传星图中 ...")
        upload_url = 'https://nova.astrometry.net/api/upload'
        upload_data = {
            'request-json': json.dumps({
                "session": session,
                "publicly_visible": "y",
                "scale_units": "degwidth",
                "scale_lower": 0.1,
                "scale_upper": 180,
            })
        }
        res = req.post(upload_url,
                       files={'file': ('star.jpg', file_bytes)},
                       data=upload_data, timeout=60)
        sub_id = res.json().get('subid')
        if not sub_id:
            return False, 0, 0, 0, 0, "上传失败"

        _report("⏳ 等待服务器解析 ...")
        status_url = f'https://nova.astrometry.net/api/submissions/{sub_id}'
        job_id = None

        # Phase 1: 等待获取 job_id (最多 60 秒)
        for i in range(20):
            time.sleep(3)
            _report(f"⏳ 等待分配任务 ... ({(i+1)*3}s)")
            try:
                sub_res = req.get(status_url, timeout=10).json()
            except Exception:
                continue
            job_ids = sub_res.get('jobs', [])
            if job_ids and job_ids[0] is not None:
                job_id = job_ids[0]
                break
        if not job_id:
            return False, 0, 0, 0, 0, "等待超时: 未获取任务ID"

        # Phase 2: 轮询 job 状态 (最多 90 秒)
        _report(f"🔍 解析中 (Job #{job_id}) ...")
        job_url = f'https://nova.astrometry.net/api/jobs/{job_id}'
        for i in range(30):
            time.sleep(3)
            _report(f"🔍 解析中 ... ({(i+1)*3}s)")
            try:
                job_res = req.get(job_url, timeout=10).json()
            except Exception:
                continue

            status = job_res.get('status', '')
            if status == 'failure':
                return False, 0, 0, 0, 0, "解析失败: 无法匹配星图"
            elif status == 'success':
                # 获取结果
                _report("✅ 匹配成功! 获取坐标 ...")
                cal_res = req.get(f'{job_url}/calibration', timeout=10).json()
                info_res = req.get(f'{job_url}/info/', timeout=10).json()
                if cal_res and cal_res.get('ra') is not None:
                    ra, dec = cal_res.get('ra'), cal_res.get('dec')
                    az, alt = get_az_alt(ra, dec)
                    objs = info_res.get('objects_in_field', [])
                    label = ", ".join(objs[:3]) if objs else "Star Field"
                    return True, ra, dec, az, alt, label
                return False, 0, 0, 0, 0, "校准数据为空"

        return False, 0, 0, 0, 0, "解析超时 (>90s)"
    except Exception as e:
        return False, 0, 0, 0, 0, str(e)


# ===========================
# 3. App 界面 UI — 适配 Flet 0.80.5 (1.0 Beta)
# ===========================
def main(page: ft.Page):
    threading.Thread(target=update_location_from_network, daemon=True).start()

    try:
        page.title = "StarLink Pro"
        page.theme_mode = ft.ThemeMode.DARK
        page.padding = 20
        page.scroll = ft.ScrollMode.AUTO
        page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

        # 桌面端设置窗口大小
        try:
            if hasattr(page, 'window') and hasattr(page.window, 'width'):
                page.window.width = 390
                page.window.height = 844
                page.window.resizable = False
                page.window.always_on_top = True
        except Exception:
            pass

        # ---- UI 组件 ----
        header_time_loc = ft.Text(
            "正在同步卫星定位与时间...",
            color="#80DEEA", size=12, text_align=ft.TextAlign.CENTER,
        )
        status_text = ft.Text(
            "🚀 Ready / 系统就绪", color="#4CAF50", size=14,
            weight=ft.FontWeight.BOLD,
        )
        guide_text = ft.Text(
            "AI Vision / 自动识别结果", color="#9C27B0", size=16,
            weight=ft.FontWeight.BOLD,
        )
        object_info = ft.Text("Waiting for image...", color="#FFFFFF", size=14)
        time_stamp = ft.Text("", color="#BDBDBD", size=12, visible=False)

        ip_input = ft.TextField(
            label="ESP32 IP", value="192.168.68.107", border_color="#00BCD4",
        )
        ra_input = ft.TextField(label="RA (deg) / 赤经", expand=True)
        dec_input = ft.TextField(label="Dec (deg) / 赤纬", expand=True)
        az_input = ft.TextField(label="Az / 方位角", expand=True, read_only=True)
        alt_input = ft.TextField(
            label="Alt / 地平高度", expand=True, read_only=True)
        manual_path_input = ft.TextField(label="手动填入图片路径", expand=True)

        # ---- FilePicker (Flet 0.80: Service, async API) ----
        file_picker = ft.FilePicker()

        # ---- 实时时钟 ----
        def update_clock():
            while True:
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                header_time_loc.value = (
                    f"📍 实时位置 ({OBSERVER_LAT:.2f}°N, {OBSERVER_LON:.2f}°E)\n"
                    f"🕒 {current_time}"
                )
                try:
                    page.update()
                except Exception:
                    break
                time.sleep(1)

        # ---- 坐标联动 ----
        def on_coords_change(e):
            if ra_input.value and dec_input.value:
                try:
                    az, alt = get_az_alt(ra_input.value, dec_input.value)
                    az_input.value = f"{az:.2f}°"
                    alt_input.value = f"{alt:.2f}°"
                    page.update()
                except Exception:
                    pass

        ra_input.on_change = on_coords_change
        dec_input.on_change = on_coords_change

        # ---- AI 识别处理 ----
        async def start_processing(file_path=None, file_bytes=None):
            if not file_path and not file_bytes:
                status_text.value = "❌ 未选择文件"
                status_text.color = "#F44336"
                page.update()
                return

            object_info.value = "Analyzing star map..."
            status_text.value = "⏳ Processing AI Analysis..."
            status_text.color = "#FF9800"
            page.update()

            # 共享进度消息列表（线程安全：只有后台线程 append，主线程 read）
            progress_messages = []

            def blocking_solve():
                """在线程中执行耗时的网络请求"""
                def progress_cb(msg):
                    progress_messages.append(msg)
                try:
                    success, ra, dec, az, alt, msg = solve_star_image(
                        file_path=file_path.strip().strip('"') if file_path else None,
                        file_bytes=file_bytes,
                        progress_cb=progress_cb,
                    )
                    return ("ok", success, ra, dec, az, alt, msg)
                except Exception as ex:
                    return ("error", str(ex))

            import concurrent.futures
            loop = asyncio.get_event_loop()
            future = loop.run_in_executor(None, blocking_solve)

            # 轮询：等待结果的同时实时显示进度
            shown = 0
            while not future.done():
                await asyncio.sleep(0.5)
                if len(progress_messages) > shown:
                    status_text.value = progress_messages[-1]
                    status_text.color = "#FF9800"
                    shown = len(progress_messages)
                    page.update()

            result = future.result()

            if result[0] == "ok":
                _, success, ra, dec, az, alt, msg = result
                if success:
                    ra_input.value = f"{ra:.4f}"
                    dec_input.value = f"{dec:.4f}"
                    az_input.value = f"{az:.2f}°"
                    alt_input.value = f"{alt:.2f}°"
                    object_info.value = f"Target: {msg}"
                    time_stamp.visible = True
                    time_stamp.value = f"Resolved: {datetime.now().strftime('%H:%M:%S')}"
                    send_udp_command(ip_input.value, ra, dec)
                    status_text.value = "✨ Match Found & Sent!"
                    status_text.color = "#00BCD4"
                else:
                    object_info.value = "Analysis Failed"
                    status_text.value = f"❌ {msg}"
                    status_text.color = "#F44336"
            else:
                _, err_msg = result
                object_info.value = "Analysis Error"
                status_text.value = f"❌ 异常: {err_msg}"
                status_text.color = "#F44336"

            page.update()

        # ---- 选择文件 (Flet 0.80: async pick_files 直接返回文件) ----
        async def on_pick_files_click(e):
            try:
                files = await file_picker.pick_files(
                    allowed_extensions=["jpg", "jpeg", "png", "bmp", "tiff"],
                )
                if files and len(files) > 0:
                    picked = files[0]
                    fp = getattr(picked, 'path', None)
                    fb = getattr(picked, 'bytes', None)

                    if fp and os.path.exists(fp):
                        # 桌面端 / 能直接读取的路径
                        await start_processing(file_path=fp)
                    elif fb:
                        # Android: path 可能为空，用 bytes
                        status_text.value = "📱 读取图片数据 ..."
                        status_text.color = "#FF9800"
                        page.update()
                        # 保存到临时文件供上传
                        import tempfile
                        tmp = os.path.join(
                            tempfile.gettempdir(), "starlink_upload.jpg")
                        with open(tmp, 'wb') as wf:
                            wf.write(fb)
                        await start_processing(file_path=tmp, file_bytes=fb)
                    elif fp:
                        # path 存在但 os.path.exists 为 False（可能是 content URI）
                        # 尝试直接传路径
                        await start_processing(file_path=fp)
                    else:
                        status_text.value = "❌ 无法获取文件 (path 和 bytes 都为空)"
                        status_text.color = "#F44336"
                        page.update()
                else:
                    status_text.value = "⚠️ 未选择文件"
                    status_text.color = "#FF9800"
                    page.update()
            except Exception as ex:
                status_text.value = f"❌ FilePicker: {ex}"
                status_text.color = "#F44336"
                page.update()

        # ---- 快捷追踪 ----
        def on_star_click(e):
            name = e.control.data
            ra, dec, az, alt = get_star_coords(name)
            ra_input.value = f"{ra:.4f}"
            dec_input.value = f"{dec:.4f}"
            az_input.value = f"{az:.2f}°"
            alt_input.value = f"{alt:.2f}°"
            object_info.value = f"Target: {name} (Locked)"
            time_stamp.visible = True
            time_stamp.value = f"Updated: {datetime.now().strftime('%H:%M:%S')}"
            _, msg = send_udp_command(ip_input.value, ra, dec)
            status_text.value = msg
            status_text.color = "#00BCD4"
            page.update()

        # ---- 手动发送 ----
        def on_send_click(e):
            status_text.value = "Sending..."
            status_text.color = "#FF9800"
            page.update()

            success, msg = send_udp_command(
                ip_input.value, ra_input.value, dec_input.value
            )
            status_text.value = msg
            status_text.color = "#00BCD4" if success else "#F44336"
            page.update()

        # ---- 布局 ----
        page.add(
            header_time_loc,
            ft.Text(
                "StarLink Pro", size=26,
                weight=ft.FontWeight.BOLD, color="#00BCD4",
            ),
            ft.Divider(height=10),
            ip_input,
            ft.Text("Quick Track / 快捷追踪", size=15, weight=ft.FontWeight.BOLD),
            ft.Row([
                ft.ElevatedButton(
                    content=ft.Text("Sun"),
                    data="Sun", on_click=on_star_click,
                    bgcolor="#FF9800", color="#FFFFFF", expand=True,
                ),
                ft.ElevatedButton(
                    content=ft.Text("Moon"),
                    data="Moon", on_click=on_star_click,
                    bgcolor="#616161", color="#FFFFFF", expand=True,
                ),
                ft.ElevatedButton(
                    content=ft.Text("Mars"),
                    data="Mars", on_click=on_star_click,
                    bgcolor="#F44336", color="#FFFFFF", expand=True,
                ),
            ]),
            ft.Divider(height=10),
            ft.Container(
                content=ft.Column(
                    [guide_text, object_info, time_stamp],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=5,
                ),
                padding=15,
                width=350,
                bgcolor="#111111",
                border=ft.border.all(2, "#9C27B0"),
                border_radius=15,
            ),
            ft.ElevatedButton(
                content=ft.Text("Select Photo / 自动识别"),
                icon=ft.Icons.PHOTO_CAMERA,
                on_click=on_pick_files_click,
                bgcolor="#9C27B0",
                color="#FFFFFF",
                width=350,
                height=50,
            ),
            ft.Row([
                manual_path_input,
                ft.IconButton(
                    icon=ft.Icons.SEARCH,
                    on_click=lambda _: start_processing(
                        manual_path_input.value),
                    bgcolor="#607D8B",
                    icon_color="#FFFFFF",
                ),
            ]),
            ft.Row([ra_input, dec_input]),
            ft.Row([az_input, alt_input]),
            ft.ElevatedButton(
                content=ft.Text("Send to Motors / 手动发送"),
                icon=ft.Icons.SEND,
                on_click=on_send_click,
                width=350,
                height=45,
                bgcolor="#2196F3",
                color="#FFFFFF",
            ),
            ft.Card(
                content=ft.Container(
                    content=status_text,
                    padding=10,
                    bgcolor="#1a1a1a",
                    border_radius=10,
                    width=350,
                ),
            ),
            ft.Container(
                content=ft.Text(
                    "✨ AI Star Field Solving Powered by Astrometry.net API",
                    color="#9E9E9E",
                    size=10,
                    italic=True,
                    text_align=ft.TextAlign.CENTER,
                ),
                margin=ft.margin.only(top=10, bottom=20),
            ),
        )

        page.update()
        threading.Thread(target=update_clock, daemon=True).start()

    except Exception:
        err = traceback.format_exc()
        print(f"FATAL ERROR:\n{err}")
        try:
            page.add(ft.Text(err, color="#E57373"))
            page.update()
        except Exception:
            pass


if __name__ == '__main__':
    # Flet 0.80+ 推荐 ft.run()，ft.app() 也仍可用
    try:
        ft.run(main)
    except AttributeError:
        ft.app(target=main)
