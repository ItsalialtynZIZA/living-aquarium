const fishList = document.getElementById("fish-list");
const fishCount = document.getElementById("fish-count");
const siteName = document.getElementById("site-name");
const clearAllButton = document.getElementById("clear-all-button");
const refreshButton = document.getElementById("refresh-button");
const messageBox = document.getElementById("message");


function showMessage(text, isError = false) {

    messageBox.textContent = text;

    messageBox.classList.remove("hidden");

    if (isError) {
        messageBox.classList.add("error");
    } else {
        messageBox.classList.remove("error");
    }

    setTimeout(() => {
        messageBox.classList.add("hidden");
    }, 3000);
}


async function loadSite() {

    try {

        const response = await fetch("/api/admin/site");

        if (response.status === 401) {
            window.location.href = "/login";
            return;
        }

        if (response.status === 403) {
            showMessage(
                "Недостаточно прав для доступа к админ-панели.",
                true
            );
            return;
        }

        const data = await response.json();

        if (data.status !== "ok") {
            showMessage(
                data.message || "Не удалось получить площадку.",
                true
            );
            return;
        }

        const site = data.site;

        siteName.textContent =
            site.name ||
            `Площадка №${site.id}`;

    } catch (error) {

        console.error(
            "Ошибка загрузки площадки:",
            error
        );

        showMessage(
            "Ошибка соединения с сервером.",
            true
        );
    }
}


async function loadFishes() {

    fishList.innerHTML = `
        <div class="loading">
            Загрузка рыбок...
        </div>
    `;

    try {

        const response = await fetch(
            "/api/admin/fishes"
        );

        if (response.status === 401) {
            window.location.href = "/login";
            return;
        }

        if (response.status === 403) {
            fishList.innerHTML = `
                <div class="empty">
                    Доступ запрещён.
                </div>
            `;
            return;
        }

        const data = await response.json();

        if (data.status !== "ok") {
            throw new Error(
                data.message ||
                "Не удалось загрузить рыбок."
            );
        }

        fishCount.textContent = data.count;

        renderFishes(data.fishes);

    } catch (error) {

        console.error(
            "Ошибка загрузки рыбок:",
            error
        );

        fishList.innerHTML = `
            <div class="empty">
                Не удалось загрузить рыбок.
            </div>
        `;

        showMessage(
            "Ошибка соединения с сервером.",
            true
        );
    }
}


function renderFishes(fishes) {

    fishList.innerHTML = "";

    if (!fishes || fishes.length === 0) {

        fishList.innerHTML = `
            <div class="empty">
                На экране сейчас нет рыбок.
            </div>
        `;

        return;
    }


    fishes.forEach((fish) => {

        const card = document.createElement("div");

        card.className = "fish-card";

        card.innerHTML = `
            <div class="fish-preview">
                <img
                    src="${fish.url}"
                    alt="Рыбка ${fish.id}"
                >
            </div>

            <div class="fish-info">

                <div class="fish-id">
                    Рыбка №${fish.id}
                </div>

                <div class="fish-filename">
                    ${fish.filename}
                </div>

                <button
                    class="remove-button"
                    data-fish-id="${fish.id}"
                >
                    Убрать с экрана
                </button>

            </div>
        `;


        const removeButton =
            card.querySelector(".remove-button");


        removeButton.addEventListener(
            "click",
            () => removeFish(
                fish.id,
                removeButton
            )
        );


        fishList.appendChild(card);

    });
}


async function removeFish(
    fishId,
    button
) {

    const confirmed = confirm(
        `Убрать рыбку №${fishId} с экрана?`
    );

    if (!confirmed) {
        return;
    }


    button.disabled = true;

    button.textContent = "Удаление...";


    try {

        const response = await fetch(
            `/api/admin/fishes/${fishId}/remove`,
            {
                method: "POST"
            }
        );


        if (response.status === 401) {
            window.location.href = "/login";
            return;
        }


        const data = await response.json();


        if (!response.ok) {

            throw new Error(
                data.detail ||
                "Не удалось удалить рыбку."
            );
        }


        showMessage(
            "Рыбка убрана с экрана."
        );


        await loadFishes();


    } catch (error) {

        console.error(
            "Ошибка удаления:",
            error
        );

        showMessage(
            error.message ||
            "Ошибка удаления рыбки.",
            true
        );


        button.disabled = false;

        button.textContent =
            "Убрать с экрана";
    }
}


async function clearAllFishes() {

    const confirmed = confirm(
        "Удалить ВСЕХ рыбок с экрана?"
    );

    if (!confirmed) {
        return;
    }


    clearAllButton.disabled = true;

    clearAllButton.textContent =
        "УДАЛЕНИЕ...";


    try {

        const response = await fetch(
            "/api/admin/fishes/clear",
            {
                method: "POST"
            }
        );


        if (response.status === 401) {
            window.location.href = "/login";
            return;
        }


        const data = await response.json();


        if (!response.ok) {

            throw new Error(
                data.detail ||
                "Не удалось удалить рыбок."
            );
        }


        showMessage(
            `Удалено рыбок: ${data.removed_count}`
        );


        await loadFishes();


    } catch (error) {

        console.error(
            "Ошибка очистки:",
            error
        );

        showMessage(
            error.message ||
            "Ошибка удаления рыбок.",
            true
        );

    } finally {

        clearAllButton.disabled = false;

        clearAllButton.textContent =
            "УДАЛИТЬ ВСЕХ РЫБОК";
    }
}


refreshButton.addEventListener(
    "click",
    async () => {
        await loadFishes();
    }
);


clearAllButton.addEventListener(
    "click",
    clearAllFishes
);


// Первоначальная загрузка

loadSite();
loadFishes();