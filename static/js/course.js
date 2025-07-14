document.addEventListener("DOMContentLoaded", () => {
    const ctx = document.getElementById("wrChart").getContext("2d");

    function parseTimeString(timeStr) {
        const match = timeStr.match(/(\d+)[’'](\d+)[”"](\d+)/);
        if (match) {
            const min = parseInt(match[1], 10);
            const sec = parseInt(match[2], 10);
            const milli = parseInt(match[3], 10);
            return min * 60 + sec + milli / 1000;
        }

        const altMatch = timeStr.match(/(\d+)[”"](\d+)/);
        if (altMatch) {
            const sec = parseInt(altMatch[1], 10);
            const milli = parseInt(altMatch[2], 10);
            return sec + milli / 1000;
        }

        console.warn("Unrecognized time format:", timeStr);
        return NaN;
    }

    // グラフ用に現WR（先頭）を除いた履歴を取得
    const slicedData = historyData.slice(1);

    const labels = slicedData.map(entry => entry.date);
    const timesInSeconds = slicedData.map(entry => parseTimeString(entry.time));

    // キャンバス横幅を調整（1点あたり60pxで自動計算）
    const canvas = document.getElementById("wrChart");
    canvas.width = labels.length * 60;

    new Chart(ctx, {
        type: "line",
        data: {
            labels: labels,
            datasets: [{
                label: "WRタイム（秒）",
                data: timesInSeconds,
                borderColor: "blue",
                backgroundColor: "rgba(0, 0, 255, 0.1)",
                fill: false,
                tension: 0.1,
                pointRadius: 3,
                pointHoverRadius: 6
            }]
        },
        options: {
            responsive: false,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: false,
                    title: {
                        display: true,
                        text: "タイム（秒）"
                    }
                }
            },
            plugins: {
                tooltip: {
                    callbacks: {
                        label: (context) => {
                            const raw = context.raw;
                            if (raw == null) return "Pre-release";
                            const min = Math.floor(raw / 60);
                            const sec = Math.floor(raw % 60);
                            const ms = Math.round((raw - Math.floor(raw)) * 1000);
                            return `${min}'${sec}"${ms.toString().padStart(3, "0")}`;
                        }
                    }
                }
            }
        }
    });
});
