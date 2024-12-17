// 심박수 데이터 가져와서 차트 생성
fetch("/api/heart_rate")
    .then(response => response.json())
    .then(data => {
        const ctx = document.getElementById("heartRateChart").getContext("2d");
        new Chart(ctx, {
            type: "line",
            data: {
                labels: data.dates, // 날짜 레이블
                datasets: [
                    { label: "Avg Heart Rate", data: data.rates.map(r => r[0]), borderColor: "blue", fill: false },
                    { label: "Max Heart Rate", data: data.rates.map(r => r[1]), borderColor: "red", fill: false },
                    { label: "Min Heart Rate", data: data.rates.map(r => r[2]), borderColor: "green", fill: false }
                ]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: { display: true }
                }
            }
        });
    });

// 걸음 수 데이터 가져와서 차트 생성
fetch("/api/steps")
    .then(response => response.json())
    .then(data => {
        const ctx = document.getElementById("stepCountChart").getContext("2d");
        new Chart(ctx, {
            type: "bar",
            data: {
                labels: data.dates, // 날짜 레이블
                datasets: [
                    { label: "Steps", data: data.steps, backgroundColor: "skyblue" }
                ]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: { display: true }
                }
            }
        });
    });
