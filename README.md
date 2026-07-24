# MARE İDA — Otonom İnsansız Deniz Aracı (USV)

İnsansız Deniz Aracı için geliştirilen otonom su üstü aracı yazılımı.
ROS 2 Humble üzerinde, VRX (Gazebo Garden) + ArduPilot SITL simülasyonunda çalışır.

## Demo

![Parkur-1 waypoint takibi](media/waypoint_takibi.gif)

*ArduRover AUTO modunda 4 köşeli dikdörtgen waypoint dizisinin takibi — VRX + ArduPilot SITL, 8× hızlandırılmış*


![Harita üzerinden hedef noktaya seyir](media/harita_hedef.gif)

*QGroundControl haritasından işaretlenen noktaya otonom seyir*
---

## Durum

**Simülasyon aşamasında — kısmen tamamlandı.**

Waypoint takibi (Parkur-1) simülasyonda uçtan uca çalışır durumda. Engelden kaçınma,
görev yöneticisi ve gerçek donanım entegrasyonu tamamlanamadı; yarışma teslim tarihine
araç donanımı yetişmediği için proje simülasyon aşamasında durdu.

| Bileşen | Durum |
|---|---|
| ROS 2 paket yapısı + walking skeleton | ✅ |
| ArduPilot SITL + MAVROS köprüsü | ✅ |
| VRX ↔ ArduPilot fizik köprüsü | ✅ |
| Lokalizasyon (ArduPilot EKF3 → ROS 2) | ✅ |
| Waypoint takibi (ArduRover AUTO) | ✅ |
| Algılama (STUB) | ⚠️ iskelet hazır, gerçek model takılmadı |
| Engelden kaçınma (A* + APF) | ❌ |
| Görev yöneticisi / parkur geçişleri | ❌ |
| Donanım entegrasyonu (Jetson / Pixhawk) | ❌ |

---

## Demo

Simülasyon kayıtları: [`media/`](media/)

---

## Mimari

İki katmanlı hiyerarşik yapı:

- **Alt katman — ArduPilot (SITL / Pixhawk):** skid-steer motor kontrolü, L1 waypoint
  navigasyonu, EKF3 durum kestirimi, mod yönetimi, failsafe'ler.
- **Üst katman — ROS 2 Humble:** algılama, karar verme, planlama, veri kayıt.
- İki katman **MAVROS (MAVLink)** üzerinden bağlanır.

**Sim-first ilkesi:** Algoritma node'ları simülasyonda ve gerçek donanımda **aynı** kalır;
yalnızca sürücü katmanı değişir (sim kamera ↔ stereo kamera, SITL ↔ Pixhawk).
Bu ayrımı korumak için topic isimleri/tipleri sabit bir arayüz sözleşmesi üzerinden
tanımlanır — node'lar donanım varsayımı içermez.

### Paket yapısı

```
src/
├── mare_bringup/       launch dosyaları, sim overlay, config
├── mare_perception/    kamera arayüzü, nesne tespiti, derinlik füzyonu
├── mare_localization/  MAVROS köprüsü
├── mare_planning/      yol planlama (A* + APF) — iskelet
├── mare_control/       cmd_vel → MAVROS GUIDED setpoint
└── mare_mission/       görev yükleme, parkur state machine — kısmi
```

### Parkur görevleri (yarışma kapsamı)

1. **Parkur-1 — Waypoint takibi:** ArduRover AUTO modunda sıralı nokta takibi. ✅
2. **Parkur-2 — Engelden kaçınma:** engel tespiti + dinamik cost map + A*/APF planlama. ❌
3. **Parkur-3 — Angajman:** renk parametreli hedef tespiti + üç fazlı yaklaşma. ❌

---

## Teknoloji Yığını

| Katman | Seçim |
|---|---|
| OS | Ubuntu 22.04 LTS (WSL2) |
| Middleware | ROS 2 Humble |
| Dil | Python (rclpy) |
| Build | colcon (`ament_python`) |
| Simülasyon | VRX (`humble` branch) + Gazebo Garden |
| Otopilot | ArduPilot SITL (Rover, `rover-skid`) |
| Köprü | MAVROS (MAVLink) |
| Fizik köprüsü | `ardupilot_gazebo` (JSON FDM) |

---

## Kurulum

### Önkoşullar

- Ubuntu 22.04 + ROS 2 Humble
- [VRX](https://github.com/osrf/vrx) (`humble` branch, Gazebo Garden) → `~/vrx_ws`
- [ArduPilot](https://github.com/ArduPilot/ardupilot) → `~/ardupilot`
- [`ardupilot_gazebo`](https://github.com/ArduPilot/ardupilot_gazebo) → `GZ_VERSION=garden` ile derlenmiş
- MAVROS (`ros-humble-mavros`, `ros-humble-mavros-extras` + GeographicLib veri setleri)

### Derleme

```bash
git clone https://github.com/seydaoksuzoglu/mare-ida.git ~/mare_ws
cd ~/mare_ws
colcon build --symlink-install
source install/setup.bash
```

---

## Çalıştırma

Her terminalde önce ortamı kur (sıra önemli):

```bash
source /opt/ros/humble/setup.bash
source ~/vrx_ws/install/setup.bash
source ~/mare_ws/install/setup.bash
```

**T1 — Gazebo (VRX):**
```bash
ros2 launch vrx_gz competition.launch.py \
  world:=sydney_regatta headless:=True \
  urdf:="$(ros2 pkg prefix mare_bringup)/share/mare_bringup/sim_overlay/wamv_ardupilot.urdf.xacro"
```

**T2 — ArduPilot SITL:**
```bash
cd ~/ardupilot
./Tools/autotest/sim_vehicle.py -v Rover -f rover-skid \
  --model JSON:127.0.0.1 --console \
  --out=127.0.0.1:14550 \
  --custom-location='-33.724223,150.679736,0.0,0'
```

GPS fix geldikten sonra MAVProxy konsolunda:
```
param set ARMING_CHECK 0
param set WP_SPEED 1.5
param set WP_RADIUS 1.5
```

**T3 — MAVROS:**
```bash
ros2 launch mare_bringup mavros_sitl.launch.py
```

**T4 — Waypoint yükle ve AUTO'ya geç:**
```bash
ros2 run mare_mission waypoint_loader_node

ros2 service call /mavros/cmd/arming mavros_msgs/srv/CommandBool "{value: true}"
ros2 service call /mavros/set_mode mavros_msgs/srv/SetMode "{custom_mode: 'AUTO'}"
```

**İzleme:**
```bash
ros2 topic echo /mavros/mission/reached
ros2 topic echo /mavros/local_position/pose
```

Waypoint koordinatları `src/mare_mission/config/parkur1_waypoints.yaml` içinde tanımlıdır.

---

## Kurulum Notları

Geliştirme sırasında karşılaşılan, dokümante edilmemiş birkaç tuzak:

- **WSL2 + hibrit grafik:** Mesa katmanı varsayılan olarak entegre GPU'yu seçebiliyor
  ve simülasyon donuyor. Çözüm: `~/.bashrc`'ye `export MESA_D3D12_DEFAULT_ADAPTER_NAME="NVIDIA"`.
  Doğrulama: `glxinfo | grep "OpenGL renderer"`. `LIBGL_ALWAYS_SOFTWARE` kullanmayın — render'ı
  CPU'ya düşürür.
- **WSL2 ağ:** `sim_vehicle.py` çıkış portlarını WSL sanal IP'sine yönlendirebiliyor;
  `--out=127.0.0.1:14550` ile açıkça loopback'e zorlayın, aksi halde MAVROS heartbeat almaz.
- **`colcon --symlink-install`:** `setup.py`'ye yeni bir dosya glob'u eklendiğinde `install/`
  altında symlink yerine bayat kopya oluşabiliyor. Değişiklik yansımıyorsa `install/` altındaki
  kopyayı silip yeniden derleyin.
- **SITL parametreleri** her yeniden başlatmada sıfırlanır (`reboot` dahil).

---

## Teşekkür / Atıf

- Araç modeli ve deniz ortamı: [VRX](https://github.com/osrf/vrx) (Open Robotics, Apache-2.0).
  `mare_bringup/sim_overlay/wamv_ardupilot.urdf.xacro`, VRX'in `wamv_gazebo.urdf.xacro`
  dosyasının ArduPilot eklentisi eklenmiş bir türevidir.
- Otopilot: [ArduPilot](https://ardupilot.org/) ve
  [`ardupilot_gazebo`](https://github.com/ArduPilot/ardupilot_gazebo).

## Lisans

Apache-2.0
