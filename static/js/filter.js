document.addEventListener("DOMContentLoaded", () => {
    const filters = {
        course: document.getElementById("courseFilter"),
        player: document.getElementById("playerFilter"),
        nation: document.getElementById("nationFilter"),
        character: document.getElementById("characterFilter"),
        vehicle: document.getElementById("vehicleFilter"),
    };

    const rows = document.querySelectorAll("#wrTable tbody tr");

    Object.values(filters).forEach(input => {
        input.addEventListener("input", () => {
            const keyword = {
                course: filters.course.value.toLowerCase(),
                player: filters.player.value.toLowerCase(),
                nation: filters.nation.value.toLowerCase(),
                character: filters.character.value.toLowerCase(),
                vehicle: filters.vehicle.value.toLowerCase(),
            };

            rows.forEach(row => {
                const cells = row.querySelectorAll("td");
                const values = {
                    course: cells[0].textContent.toLowerCase(),
                    player: cells[2].textContent.toLowerCase(),
                    nation: cells[3].textContent.toLowerCase(),
                    character: cells[5].textContent.toLowerCase(),
                    vehicle: cells[6].textContent.toLowerCase(),
                };

                const visible = Object.keys(keyword).every(key =>
                    values[key].includes(keyword[key])
                );
                row.style.display = visible ? "" : "none";
            });
        });
    });
});
