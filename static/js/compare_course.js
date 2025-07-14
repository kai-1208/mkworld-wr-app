function compareSelected() {
    const checkboxes = document.querySelectorAll(".compare-checkbox:checked");
    const compareArea = document.getElementById("compareArea");
    compareArea.innerHTML = "";

    if (checkboxes.length === 0 || checkboxes.length > 3) {
        alert("比較は1〜3件まで選択してください");
        return;
    }

    checkboxes.forEach(cb => {
        const record = JSON.parse(cb.dataset.record);
        const div = document.createElement("div");
        div.className = "ranking-box";

        const lapText = record.laps.join(", ");

        div.innerHTML = `
            <h3>${record.date}</h3>
            <p><strong>Time:</strong> ${record.time}</p>
            <p><strong>Player:</strong> ${record.player} (${record.nation})</p>
            <p><strong>Lap Times:</strong> ${lapText}</p>
            <p><strong>Coins:</strong> ${record.coins}</p>
            <p><strong>Shrooms:</strong> ${record.shrooms}</p>
            <p><strong>Character:</strong> ${record.character}</p>
            <p><strong>Kart:</strong> ${record.kart}</p>
        `;

        compareArea.appendChild(div);
    });
}
