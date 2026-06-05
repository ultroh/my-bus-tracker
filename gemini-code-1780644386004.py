import zipfile
import os

# Create directory structure
repo_dir = "kaist-commuter-bus-tracker"
os.makedirs(repo_dir, exist_ok=True)

# 1. index.html
html_content = """<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>KAIST 통근버스 실시간 위치 예측 시스템</title>
    <link rel="stylesheet" href="style.css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
</head>
<body>
    <div class="app-container">
        <header>
            <div class="logo-area">
                <i class="fa-solid fa-bus-simple main-icon"></i>
                <div>
                    <h1>KAIST 통근버스</h1>
                    <p>시간표 기반 실시간 위치 예측 시스템</p>
                </div>
            </div>
            <div class="system-status">
                <span class="status-badge"><i class="fa-solid fa-circle-check"></i> 정상 운영</span>
            </div>
        </header>

        <main>
            <section class="control-panel">
                <div class="mode-selector">
                    <button id="btn-morning" class="mode-btn active" onclick="setMode('morning')">
                        <i class="fa-solid fa-sun"></i> 출근 노선 (07:30 ~ 08:40)
                    </button>
                    <button id="btn-evening" class="mode-btn" onclick="setMode('evening')">
                        <i class="fa-solid fa-moon"></i> 퇴근 노선 (18:00 ~ 19:15)
                    </button>
                </div>

                <div class="time-simulator">
                    <div class="slider-header">
                        <span class="label"><i class="fa-solid fa-clock"></i> 시뮬레이션 시간 선택</span>
                        <span id="timeDisplay" class="time-digital">07:30</span>
                    </div>
                    <div class="slider-wrapper">
                        <input type="range" id="timeSlider" min="0" max="75" value="0" oninput="updateTime()">
                        <div class="slider-ticks">
                            <span id="tick-start">07:30</span>
                            <span id="tick-mid">08:00</span>
                            <span id="tick-end">08:45</span>
                        </div>
                    </div>
                </div>
                
                <div class="info-banner">
                    <i class="fa-solid fa-circle-info"></i>
                    <p>본 시스템은 학내 공식 시간표 데이터를 기반으로 버스의 현재 예상 위치를 실시간 보간 계산(Interpolation)하여 보여줍니다. 도로 교통 사정에 따라 <strong>±5분 내외의 오차</strong>가 발생할 수 있습니다.</p>
                </div>
            </section>

            <section class="tracking-monitor">
                <div class="bus-card card-1">
                    <div class="card-header">
                        <div class="bus-title">
                            <span class="badge b-1">1호차</span>
                            <h2 id="route-name-1">복합터미널 ➔ KAIST</h2>
                        </div>
                        <div class="live-status" id="status1">대기 중...</div>
                    </div>
                    <div class="timeline-container">
                        <div class="timeline-track">
                            <div id="stops1" class="stops-wrapper"></div>
                            <div class="bus-marker" id="bus1">
                                <i class="fa-solid fa-bus"></i>
                                <span class="marker-pulse"></span>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="bus-card card-2">
                    <div class="card-header">
                        <div class="bus-title">
                            <span class="badge b-2">2호차</span>
                            <h2 id="route-name-2">대동 ➔ KAIST</h2>
                        </div>
                        <div class="live-status" id="status2">대기 중...</div>
                    </div>
                    <div class="timeline-container">
                        <div class="timeline-track">
                            <div id="stops2" class="stops-wrapper"></div>
                            <div class="bus-marker" id="bus2">
                                <i class="fa-solid fa-bus"></i>
                                <span class="marker-pulse"></span>
                            </div>
                        </div>
                    </div>
                </div>
            </section>
        </main>

        <footer>
            <p>© 2026 KAIST Commuter Bus Tracker Project. Powered by Timetable Interpolation Engine.</p>
            <p class="footer-notice">본 서비스는 교직원 전용 통근버스 정보를 제공하며, 탑승 시 사원증 확인이 필요할 수 있습니다.</p>
        </footer>
    </div>

    <script src="script.js"></script>
</body>
</html>
"""

# 2. style.css
css_content = """:root {
    --primary-color: #1e3a8a;
    --secondary-color: #3b82f6;
    --bg-color: #f8fafc;
    --card-bg: #ffffff;
    --text-main: #1e293b;
    --text-muted: #64748b;
    --accent-red: #ef4444;
    --accent-green: #10b981;
    --border-color: #e2e8f0;
    --bus-1-color: #0284c7;
    --bus-2-color: #7c3aed;
}

* {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif, "Apple Color Emoji", "Segoe UI Emoji";
}

body {
    background-color: var(--bg-color);
    color: var(--text-main);
    padding: 20px;
    display: flex;
    justify-content: center;
}

.app-container {
    width: 100%;
    max-width: 1000px;
    background: transparent;
}

/* Header */
header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: linear-gradient(135deg, #1e3a8a 0%, #0f172a 100%);
    color: white;
    padding: 24px;
    border-radius: 16px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
    margin-bottom: 24px;
}

.logo-area {
    display: flex;
    align-items: center;
    gap: 16px;
}

.main-icon {
    font-size: 32px;
    background: rgba(255, 255, 255, 0.15);
    padding: 12px;
    border-radius: 12px;
}

header h1 {
    font-size: 22px;
    font-weight: 700;
    letter-spacing: -0.5px;
}

header p {
    font-size: 13px;
    color: #93c5fd;
    margin-top: 2px;
}

.status-badge {
    background: rgba(16, 185, 129, 0.2);
    color: #34d399;
    padding: 6px 12px;
    border-radius: 20px;
    font-size: 13px;
    font-weight: 600;
    display: flex;
    align-items: center;
    gap: 6px;
}

/* Control Panel */
.control-panel {
    background: var(--card-bg);
    padding: 24px;
    border-radius: 16px;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    margin-bottom: 24px;
    border: 1px solid var(--border-color);
}

.mode-selector {
    display: flex;
    gap: 12px;
    margin-bottom: 24px;
}

.mode-btn {
    flex: 1;
    padding: 14px;
    font-size: 15px;
    font-weight: 600;
    border: 1px solid var(--border-color);
    background-color: #f1f5f9;
    color: var(--text-muted);
    border-radius: 10px;
    cursor: pointer;
    transition: all 0.2s ease;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
}

.mode-btn.active {
    background-color: var(--primary-color);
    color: white;
    border-color: var(--primary-color);
    box-shadow: 0 4px 12px rgba(30, 58, 138, 0.2);
}

.time-simulator {
    background: #f8fafc;
    padding: 20px;
    border-radius: 12px;
    border: 1px solid var(--border-color);
    margin-bottom: 16px;
}

.slider-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 12px;
}

.slider-header .label {
    font-size: 14px;
    font-weight: 600;
    color: var(--text-main);
}

.time-digital {
    font-size: 28px;
    font-weight: 800;
    color: var(--accent-red);
    font-family: monospace;
    background: #fee2e2;
    padding: 2px 10px;
    border-radius: 6px;
}

.slider-wrapper {
    position: relative;
    padding: 10px 0;
}

input[type="range"] {
    -webkit-appearance: none;
    width: 100%;
    height: 8px;
    border-radius: 4px;
    background: #cbd5e1;
    outline: none;
}

input[type="range"]::-webkit-slider-thumb {
    -webkit-appearance: none;
    appearance: none;
    width: 22px;
    height: 22px;
    border-radius: 50%;
    background: var(--primary-color);
    cursor: pointer;
    box-shadow: 0 2px 6px rgba(0,0,0,0.2);
    transition: transform 0.1s;
}

input[type="range"]::-webkit-slider-thumb:hover {
    transform: scale(1.15);
}

.slider-ticks {
    display: flex;
    justify-content: space-between;
    font-size: 11px;
    color: var(--text-muted);
    margin-top: 8px;
    padding: 0 4px;
}

.info-banner {
    display: flex;
    gap: 10px;
    background-color: #eff6ff;
    border-left: 4px solid var(--secondary-color);
    padding: 12px 16px;
    border-radius: 0 8px 8px 0;
    font-size: 13px;
    line-height: 1.5;
    color: #1e40af;
}

/* Bus Cards Monitoring */
.tracking-monitor {
    display: flex;
    flex-direction: column;
    gap: 20px;
}

.bus-card {
    background: var(--card-bg);
    border-radius: 16px;
    padding: 24px;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    border: 1px solid var(--border-color);
    overflow: hidden;
}

.card-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    border-bottom: 1px dashed var(--border-color);
    padding-bottom: 16px;
    margin-bottom: 40px;
}

.bus-title {
    display: flex;
    align-items: center;
    gap: 12px;
}

.badge {
    color: white;
    padding: 4px 10px;
    border-radius: 6px;
    font-size: 12px;
    font-weight: 700;
}

.badge.b-1 { background-color: var(--bus-1-color); }
.badge.b-2 { background-color: var(--bus-2-color); }

.bus-title h2 {
    font-size: 18px;
    font-weight: 700;
    color: var(--text-main);
}

.live-status {
    font-size: 13px;
    font-weight: 600;
    background: #f1f5f9;
    padding: 6px 12px;
    border-radius: 8px;
    color: var(--text-main);
}

/* Timeline Layout */
.timeline-container {
    padding: 20px 10px 40px 10px;
    position: relative;
}

.timeline-track {
    width: 100%;
    height: 6px;
    background-color: #e2e8f0;
    border-radius: 3px;
    position: relative;
}

.stops-wrapper {
    position: absolute;
    width: 100%;
    top: 0;
    left: 0;
    height: 100%;
}

.stop-node {
    position: absolute;
    top: 3px;
    transform: translate(-50%, -50%);
    display: flex;
    flex-direction: column;
    align-items: center;
}

.node-dot {
    width: 12px;
    height: 12px;
    background-color: #cbd5e1;
    border: 2px solid white;
    border-radius: 50%;
    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    transition: all 0.3s ease;
}

.stop-node.passed .node-dot {
    background-color: var(--accent-green);
}

.stop-node.next .node-dot {
    background-color: var(--accent-red);
    transform: translate(-50%, -50%) scale(1.2);
    box-shadow: 0 0 8px rgba(239, 68, 68, 0.6);
}

.node-label {
    position: absolute;
    top: 18px;
    font-size: 11px;
    font-weight: 500;
    color: var(--text-muted);
    white-space: nowrap;
    text-align: center;
    line-height: 1.3;
}

.stop-node.passed .node-label {
    color: var(--text-main);
}

.stop-node.next .node-label {
    color: var(--accent-red);
    font-weight: 700;
}

.node-time {
    display: block;
    font-size: 10px;
    color: #94a3b8;
    margin-top: 1px;
}

.stop-node.next .node-time {
    color: var(--accent-red);
}

/* Bus Marker Object */
.bus-marker {
    position: absolute;
    top: 3px;
    transform: translate(-50%, -50%);
    z-index: 10;
    display: none;
    align-items: center;
    justify-content: center;
    width: 32px;
    height: 32px;
    border-radius: 50%;
    color: white;
    box-shadow: 0 4px 10px rgba(0,0,0,0.25);
}

.card-1 .bus-marker { background-color: var(--bus-1-color); }
.card-2 .bus-marker { background-color: var(--bus-2-color); }

.bus-marker i {
    font-size: 14px;
}

.marker-pulse {
    position: absolute;
    width: 100%;
    height: 100%;
    border-radius: 50%;
    z-index: -1;
    opacity: 0.4;
    animation: pulse 1.8s infinite ease-in-out;
}

.card-1 .marker-pulse { background-color: var(--bus-1-color); }
.card-2 .marker-pulse { background-color: var(--bus-2-color); }

@keyframes pulse {
    0% { transform: scale(1); opacity: 0.5; }
    100% { transform: scale(1.8); opacity: 0; }
}

/* Footer */
footer {
    text-align: center;
    margin-top: 40px;
    padding: 20px;
    color: var(--text-muted);
    font-size: 13px;
    border-top: 1px solid var(--border-color);
}

.footer-notice {
    font-size: 11px;
    margin-top: 6px;
    color: #94a3b8;
}

/* Responsive Customization */
@media (max-width: 768px) {
    .node-label {
        transform: rotate(-35deg) translate(-12px, 0);
        text-align: right;
        white-space: nowrap;
    }
    .timeline-container {
        padding-bottom: 70px;
    }
}
"""

# 3. script.js
script_content = """// 노선 타임테이블 마스터 데이터 (분 단위 인덱스화: 출발 기준점 형성)
const config = {
    morning: {
        startHour: 7, startMinute: 30, maxSlider: 75,
        tickStart: "07:30", tickMid: "08:05", tickEnd: "08:45",
        routes: {
            title1: "출근 1호차 (시내 외곽 노선)",
            title2: "출근 2호차 (둔산 도심 노선)",
            bus1: [
                { name: "복합터미널", time: 12 }, { name: "홍도동", time: 14 }, { name: "목동", time: 20 },
                { name: "태평동오거리", time: 30 }, { name: "가장동래미안", time: 35 }, { name: "갈마동요양병원", time: 45 },
                { name: "갈마동갈비만", time: 50 }, { name: "유성온천역", time: 58 }, { name: "KAIST", time: 65 }
            ],
            bus2: [
                { name: "대동역", time: 10 }, { name: "문창동", time: 15 }, { name: "부사동야구장", time: 18 },
                { name: "대흥동중구청", time: 22 }, { name: "중촌동", time: 27 }, { name: "둔산동세이브존", time: 38 },
                { name: "정부청사역", time: 45 }, { name: "월평역", time: 55 }, { name: "궁동혜천문화사", time: 57 }, { name: "KAIST", time: 60 }
            ]
        }
    },
    evening: {
        startHour: 18, startMinute: 0, maxSlider: 75,
        tickStart: "18:00", tickMid: "18:35", tickEnd: "19:15",
        routes: {
            title1: "퇴근 1호차 (터미널 방면)",
            title2: "퇴근 2호차 (대동역 방면)",
            // 퇴근은 원내 정류장 순환계산 포함 매핑 연산 유연화 처리
            bus1: [
                { name: "교수회관(N6)", time: 7 }, { name: "대강당(E15)", time: 8 }, { name: "교육지원동(W8)", time: 9 }, { name: "오리연못", time: 10 },
                { name: "충대앞주유소", time: 15 }, { name: "유성온천역", time: 20 }, { name: "갈마동", time: 28 }, { name: "가장동", time: 38 },
                { name: "태평동", time: 43 }, { name: "목동", time: 53 }, { name: "홍도동", time: 59 }, { name: "복합터미널", time: 61 }
            ],
            bus2: [
                { name: "교수회관(N6)", time: 7 }, { name: "대강당(E15)", time: 8 }, { name: "교육지원동(W8)", time: 9 }, { name: "오리연못", time: 10 },
                { name: "월평역", time: 18 }, { name: "궁동", time: 21 }, { name: "정부청사역", time: 30 }, { name: "둔산동", time: 37 },
                { name: "중촌동", time: 48 }, { name: "대흥동", time: 53 }, { name: "부사동", time: 57 }, { name: "문창동", time: 60 }, { name: "대동역", time: 65 }
            ]
        }
    }
};

let currentMode = 'morning';

// 모드 전환 제어 함수
function setMode(mode) {
    currentMode = mode;
    document.getElementById('btn-morning').classList.toggle('active', mode === 'morning');
    document.getElementById('btn-evening').classList.toggle('active', mode === 'evening');
    
    // 슬라이더 한계점 동적 세팅 및 초기화
    const slider = document.getElementById('timeSlider');
    slider.max = config[currentMode].maxSlider;
    slider.value = 0;

    // 슬라이더 하단 가이드 시간 텍스트 변경
    document.getElementById('tick-start').innerText = config[currentMode].tickStart;
    document.getElementById('tick-mid').innerText = config[currentMode].tickMid;
    document.getElementById('tick-end').innerText = config[currentMode].tickEnd;

    // 카드 내부 타이틀 정보 갱신
    document.getElementById('route-name-1').innerText = config[currentMode].routes.title1;
    document.getElementById('route-name-2').innerText = config[currentMode].routes.title2;
    
    // 노선도 정류장 노드 재생성
    drawTimelineNodes(config[currentMode].routes.bus1, 'stops1');
    drawTimelineNodes(config[currentMode].routes.bus2, 'stops2');
    
    updateTime();
}

// 타임라인 위에 정류장 노드 배치 디자인 렌더링
function drawTimelineNodes(routeData, containerId) {
    const container = document.getElementById(containerId);
    container.innerHTML = '';
    const maxTime = routeData[routeData.length - 1].time;

    routeData.forEach((stop) => {
        let percentage = (stop.time / maxTime) * 100;
        let nodeHtml = `
            <div class="stop-node" id="node-${containerId}-${stop.time}" style="left: ${percentage}%;">
                <div class="node-dot"></div>
                <div class="node-label">
                    ${stop.name}
                    <span class="node-time">${formatDisplayTime(stop.time)}</span>
                </div>
            </div>`;
        container.innerHTML += nodeHtml;
    });
}

// 인덱스 분 단위를 "HH:MM" 디지털 포맷으로 변환 계산기
function formatDisplayTime(totalMinutes) {
    let h = config[currentMode].startHour;
    let m = config[currentMode].startMinute + totalMinutes;
    if (m >= 60) {
        h += Math.floor(m / 60);
        m = m % 60;
    }
    return `${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}`;
}

// 인풋 슬라이더 액션 연동 함수
function updateTime() {
    let sliderValue = parseInt(document.getElementById('timeSlider').value);
    document.getElementById('timeDisplay').innerText = formatDisplayTime(sliderValue);
    
    calculateInterpolation(config[currentMode].routes.bus1, sliderValue, 'bus1', 'status1', 'stops1');
    calculateInterpolation(config[currentMode].routes.bus2, sliderValue, 'bus2', 'status2', 'stops2');
}

// 시간 비례 보간 알고리즘 핵심 (Position Tracker Engine)
function calculateInterpolation(routeData, currentTime, busId, statusId, containerId) {
    let busElement = document.getElementById(busId);
    let statusElement = document.getElementById(statusId);
    let maxTime = routeData[routeData.length - 1].time;

    // 모든 노드 스타일 초기화구문
    routeData.forEach(stop => {
        let node = document.getElementById(`node-${containerId}-${stop.time}`);
        if(node) node.className = "stop-node";
    });

    // Case A: 아직 첫차 출발지점 전 대기 상태일 때
    if (currentTime < routeData[0].time) {
        busElement.style.display = 'none';
        statusElement.innerHTML = `<span style="color:#64748b;"><i class="fa-solid fa-hourglass-start"></i> 운행 대기 중</span>`;
        let firstNode = document.getElementById(`node-${containerId}-${routeData[0].time}`);
        if(firstNode) firstNode.classList.add('next');
        return;
    }
    
    // Case B: 종점 안착 및 정지 상태 (운행 종료)
    if (currentTime >= maxTime) {
        busElement.style.display = 'flex';
        busElement.style.left = '100%';
        statusElement.innerHTML = `<span style="color:#94a3b8;"><i class="fa-solid fa-flag-checkered"></i> 운행 종료</span>`;
        routeData.forEach(stop => {
            let node = document.getElementById(`node-${containerId}-${stop.time}`);
            if(node) node.classList.add('passed');
        });
        return;
    }

    // Case C: 정류장과 정류장 사이 실시간 이동 예측 보간 연산
    busElement.style.display = 'flex';
    
    for (let i = 0; i < routeData.length - 1; i++) {
        let currentStop = routeData[i];
        let nextStop = routeData[i + 1];

        // 과거 지나온 정류장 상태 노드 체크 처리
        let currentNode = document.getElementById(`node-${containerId}-${currentStop.time}`);
        if(currentNode) currentNode.classList.add('passed');

        if (currentTime >= currentStop.time && currentTime < nextStop.time) {
            // 보간법 공식 수립 (Interpolation Calculation)
            let segmentDuration = nextStop.time - currentStop.time;
            let timeElapsed = currentTime - currentStop.time;
            let progressRatio = timeElapsed / segmentDuration;

            let startPercent = (currentStop.time / maxTime) * 100;
            let endPercent = (nextStop.time / maxTime) * 100;
            
            // 선형 보간 위치 도출 값
            let currentGlobalPercent = startPercent + ((endPercent - startPercent) * progressRatio);

            // 마커 연동 이동
            busElement.style.left = `${currentGlobalPercent}%`;
            
            // 다음 정류장 타겟 포인트 시각 표출 알림 활성화
            let nextNode = document.getElementById(`node-${containerId}-${nextStop.time}`);
            if(nextNode) nextNode.classList.add('next');

            statusElement.innerHTML = `
                <span style="color:#1e40af;">
                    <i class="fa-solid fa-circle-dot-notch fa-spin"></i> 
                    <strong>${currentStop.name}</strong> 통과 ➔ <strong>${nextStop.name}</strong> 향해 이동 중
                </span>`;
            break;
        }
    }
}

// 윈도우 최초 실행 초기 구동 로드 스크립트
window.onload = function() {
    setMode('morning');
};
"""

# 4. README.md
readme_content = """# 🚌 KAIST 통근버스 시간표 기반 위치 예측 시스템 (GitHub Pages 배포용)

본 리포지토리는 **KAIST 교직원 통근버스 운행 시간표** 데이터를 바탕으로, 별도의 버스 GPS 단말기 연동 없이 **시간 비례 보간법(Time Interpolation Algorithm)**을 활용하여 버스의 현재 예상 위치를 실시간 추적 및 시각화하는 고성능 웹 대시보드 애플리케이션입니다.

---

## ✨ 핵심 기능 및 특징

1. **시간표 기반 선형 보간 알고리즘 (Timetable Interpolation)**
   - 정류장 간 운행 스케줄 시간을 실시간 가중치 분석 처리하여, 지도와 동기화 가능한 실시간 진행 트래킹 바 애니메이션을 구현했습니다.
2. **원터치 출/퇴근 노선 스위칭 가변형 UI**
   - 오전 출근 노선(1·2호차 분리 기점 순환) 및 오후 퇴근 노선(원내 정류장 출발 연동 가공) 스위치 인터페이스를 완벽하게 제공합니다.
3. **가벼운 순수 모던 웹 스택 (Vanilla Web Stack)**
   - React, Vue 등 복잡한 프레임워크 빌드 과정 없이 `HTML5`, `CSS3(Variable)`, `Pure JS` 파일 조합만으로 구동되어 로딩 속도가 극도로 빠르며, GitHub Pages 서버 환경에 최적화되어 있습니다.
4. **반응형 웹 UI (Responsive Web Design)**
   - 모바일, 태블릿, PC 등 다양한 디바이스 환경에서 흐트러짐 없는 타임라인 궤적 가독성을 확보했습니다.

---

## 📂 리포지토리 구성 파일 구조