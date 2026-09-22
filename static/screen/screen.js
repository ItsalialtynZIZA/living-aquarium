console.log("SCREEN JS ЗАПУЩЕН");

// ==================================================
// CANVAS
// ==================================================

var canvas = document.getElementById("fish-canvas");
var ctx = null;

if (canvas) {
    ctx = canvas.getContext("2d");
    console.log("CANVAS OK");
} else {
    console.error("Canvas fish-canvas не найден.");
}


// ==================================================
// ФОНОВОЕ ВИДЕО
// ==================================================

var oceanVideo =
    document.getElementById("ocean-video");


function startOceanVideo() {

    if (!oceanVideo) {

        console.error(
            "Видео ocean-video не найдено."
        );

        return;
    }

    oceanVideo.muted = true;

    var playPromise = oceanVideo.play();

    if (playPromise) {

        playPromise
            .then(function () {

                console.log(
                    "Фоновое видео запущено."
                );

            })
            .catch(function (error) {

                console.error(
                    "Не удалось запустить видео:",
                    error
                );

            });

    } else {

        console.log(
            "Команда play() выполнена."
        );

    }
}


// ==================================================
// ВИДЕО
// ==================================================

if (oceanVideo) {

    oceanVideo.muted = true;
    oceanVideo.loop = true;

    oceanVideo.addEventListener(
        "ended",
        function () {

            console.log(
                "Видео закончилось. Перезапускаем."
            );

            try {

                oceanVideo.currentTime = 0;

            } catch (error) {

                console.log(
                    "Не удалось сбросить видео:",
                    error
                );

            }

            startOceanVideo();

        }
    );


    oceanVideo.addEventListener(
        "loadeddata",
        function () {

            console.log(
                "Видео загружено."
            );

            startOceanVideo();

        }
    );


    oceanVideo.addEventListener(
        "canplay",
        function () {

            console.log(
                "Видео готово к воспроизведению."
            );

        }
    );


    startOceanVideo();
}


// ==================================================
// РАЗМЕР CANVAS
// ==================================================

function resizeCanvas() {

    if (!canvas) {
        return;
    }

    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
}


resizeCanvas();


window.addEventListener(
    "resize",
    resizeCanvas
);


// ==================================================
// РЫБКИ
// ==================================================

var fishes = [];

var fishImages = [];


// ==================================================
// ДАННЫЕ УСТРОЙСТВА
// ==================================================

var deviceSiteId = null;


// ==================================================
// ЗАГРУЗКА РЫБОК
// ==================================================

function loadFishes() {

    console.log(
        "Начинаем загрузку рыбок..."
    );

    return fetch("/api/fish")

        .then(function (response) {

            console.log(
                "API /api/fish status:",
                response.status
            );

            if (!response.ok) {

                throw new Error(
                    "Не удалось получить список рыбок."
                );

            }

            return response.json();

        })

        .then(function (data) {

            console.log(
                "Данные рыбок:",
                data
            );


            if (!data) {

                console.log(
                    "API не вернул данные."
                );

                return;
            }


            if (!data.fishes) {

                console.log(
                    "В ответе нет массива fishes."
                );

                return;
            }


            console.log(
                "Количество рыбок:",
                data.fishes.length
            );


            for (
                var i = 0;
                i < data.fishes.length;
                i++
            ) {

                var fishData =
                    data.fishes[i];


                var image =
                    new Image();


                image.onload =
                    (function (
                        loadedImage,
                        loadedFish
                    ) {

                        return function () {

                            console.log(
                                "Изображение рыбки загружено:",
                                loadedFish.id
                            );


                            fishImages.push(
                                loadedImage
                            );


                            createFish(
                                loadedImage,
                                loadedFish.direction,
                                loadedFish.id
                            );

                        };

                    })(
                        image,
                        fishData
                    );


                image.onerror =
                    (function (fishUrl) {

                        return function () {

                            console.error(
                                "Не удалось загрузить рыбку:",
                                fishUrl
                            );

                        };

                    })(
                        fishData.url
                    );


                image.src =
                    fishData.url;
            }

        })

        .catch(function (error) {

            console.error(
                "Ошибка загрузки рыбок:",
                error
            );

        });
}


// ==================================================
// СОЗДАНИЕ РЫБКИ
// ==================================================

function createFish(
    image,
    initialDirection,
    fishId
) {

    if (!canvas) {
        return;
    }


    // ==================================================
    // ГЛУБИНА
    // ==================================================

    var depth =
        Math.floor(
            Math.random() * 3
        );


    var scale;
    var speed;
    var opacity;


    if (depth === 0) {

        scale =
            0.55 +
            Math.random() * 0.2;

        speed =
            0.4 +
            Math.random() * 0.6;

        opacity =
            0.55 +
            Math.random() * 0.15;


    } else if (depth === 1) {

        scale =
            0.85 +
            Math.random() * 0.25;

        speed =
            0.7 +
            Math.random() * 0.8;

        opacity =
            0.75 +
            Math.random() * 0.15;


    } else {

        scale =
            1.15 +
            Math.random() * 0.3;

        speed =
            1.0 +
            Math.random() * 1.0;

        opacity =
            0.9 +
            Math.random() * 0.1;
    }


    // ==================================================
    // РАЗМЕР
    // ==================================================

    var baseWidth = 180;
    var baseHeight = 120;


    // ==================================================
    // НАПРАВЛЕНИЕ
    // ==================================================

    var direction;


    if (
        initialDirection === 1 ||
        initialDirection === -1
    ) {

        direction =
            initialDirection;

    } else {

        direction =
            Math.random() > 0.5
                ? 1
                : -1;
    }


    // ==================================================
    // РЫБКА
    // ==================================================

    var fish = {

        id: fishId,

        image: image,

        x:
            Math.random() *
            canvas.width,

        y:
            Math.random() *
            canvas.height,


        width:
            baseWidth *
            scale,

        height:
            baseHeight *
            scale,


        speed:
            speed,


        // Направление движения
        direction:
            direction,


        // Направление изображения
        displayDirection:
            direction,


        // Скорость разворота
        turnSpeed:
            0.04,


        time:
            Math.random() *
            Math.PI *
            2,


        waveSpeed:
            0.015 +
            Math.random() * 0.02,


        waveAmplitude:
            0.3 +
            Math.random() * 0.8,


        drift:
            (Math.random() - 0.5) *
            0.3,


        depth:
            depth,


        opacity:
            opacity

    };


    fishes.push(fish);


    console.log(
        "Рыбка создана:",
        fishId,
        "Всего:",
        fishes.length
    );
}


// ==================================================
// ОБНОВЛЕНИЕ РЫБ
// ==================================================

function updateFish(fish) {


    // ==================================================
    // ГОРИЗОНТАЛЬНОЕ ДВИЖЕНИЕ
    // ==================================================

    fish.x +=
        fish.speed *
        fish.direction;


    // ==================================================
    // ВЕРТИКАЛЬНОЕ ПЛАВАНИЕ
    // ==================================================

    fish.y +=
        Math.sin(fish.time) *
        fish.waveAmplitude;


    fish.time +=
        fish.waveSpeed;


    // ==================================================
    // НЕБОЛЬШОЕ ИЗМЕНЕНИЕ КУРСА
    // ==================================================

    fish.y +=
        Math.sin(
            fish.time * 0.7
        ) *
        fish.drift;


    // ==================================================
    // ПРАВАЯ ГРАНИЦА
    // ==================================================

    if (
        fish.direction === 1 &&
        fish.x >
        canvas.width -
        fish.width / 2
    ) {

        fish.direction = -1;

    }


    // ==================================================
    // ЛЕВАЯ ГРАНИЦА
    // ==================================================

    if (
        fish.direction === -1 &&
        fish.x <
        fish.width / 2
    ) {

        fish.direction = 1;

    }


    // ==================================================
    // ПЛАВНЫЙ РАЗВОРОТ
    // ==================================================

    fish.displayDirection +=

        (
            fish.direction -
            fish.displayDirection
        ) *
        fish.turnSpeed;
}


// ==================================================
// РИСОВАНИЕ РЫБЫ
// ==================================================

function drawFish(fish) {


    if (!fish.image) {
        return;
    }


    if (!fish.image.complete) {
        return;
    }


    ctx.save();


    // ==================================================
    // ПРОЗРАЧНОСТЬ
    // ==================================================

    ctx.globalAlpha =
        fish.opacity;


    // ==================================================
    // ПОЗИЦИЯ
    // ==================================================

    ctx.translate(
        fish.x,
        fish.y
    );


    // ==================================================
    // РАЗВОРОТ
    // ==================================================

    ctx.scale(
        fish.displayDirection,
        1
    );


    // ==================================================
    // ЛЁГКОЕ ПОКАЧИВАНИЕ
    // ==================================================

    var rotation =
        Math.sin(
            fish.time * 0.8
        ) *
        0.04;


    ctx.rotate(
        rotation
    );


    // ==================================================
    // РИСУЕМ РЫБУ
    // ==================================================

    ctx.drawImage(

        fish.image,

        -fish.width / 2,

        -fish.height / 2,

        fish.width,

        fish.height

    );


    ctx.restore();
}


// ==================================================
// АНИМАЦИЯ
// ==================================================

function animate() {


    if (!canvas || !ctx) {

        return;

    }


    // Очищаем Canvas

    ctx.clearRect(

        0,
        0,
        canvas.width,
        canvas.height

    );


    // Обновляем и рисуем всех рыб

    for (
        var i = 0;
        i < fishes.length;
        i++
    ) {

        updateFish(
            fishes[i]
        );


        drawFish(
            fishes[i]
        );

    }


    // Следующий кадр

    requestAnimationFrame(
        animate
    );
}


// ==================================================
// ЗАПУСК АНИМАЦИИ
// ==================================================

animate();


// ==================================================
// WEBSOCKET
// ==================================================

var wsProtocol =
    window.location.protocol === "https:"
        ? "wss:"
        : "ws:";


var websocket =
    new WebSocket(
        wsProtocol +
        "//" +
        window.location.host +
        "/ws/screen"
    );


// ==================================================
// WEBSOCKET CONNECTED
// ==================================================

websocket.onopen =
    function () {

        console.log(
            "WebSocket подключён."
        );

    };


// ==================================================
// ДОБАВЛЕНИЕ НОВОЙ РЫБКИ
// ==================================================

function addFishFromUrl(
    url,
    direction,
    confidence,
    fishId
) {

    console.log(
        "Начинаем загрузку новой рыбки:",
        url
    );


    console.log(
        "Направление:",
        direction,
        "Уверенность:",
        Math.round(
            confidence * 100
        ) + "%"
    );


    var image =
        new Image();


    image.onload =
        function () {

            console.log(
                "Изображение новой рыбки загружено:",
                image.width,
                "x",
                image.height
            );


            fishImages.push(
                image
            );


            createFish(
                image,
                direction,
                fishId
            );


            console.log(
                "Рыбка добавлена в массив.",
                "Всего рыбок:",
                fishes.length
            );

        };


    image.onerror =
        function (error) {

            console.error(
                "ОШИБКА загрузки новой рыбки:",
                url,
                error
            );

        };


    image.src =
        url;
}


// ==================================================
// УДАЛЕНИЕ РЫБКИ
// ==================================================

function removeFishById(
    fishId
) {

    var index = -1;


    for (
        var i = 0;
        i < fishes.length;
        i++
    ) {

        if (
            fishes[i].id ===
            fishId
        ) {

            index = i;

            break;
        }
    }


    if (index === -1) {

        console.warn(
            "Рыбка для удаления не найдена:",
            fishId
        );

        return;
    }


    fishes.splice(
        index,
        1
    );


    console.log(
        "Рыбка удалена с экрана:",
        fishId,
        "Осталось рыбок:",
        fishes.length
    );
}


// ==================================================
// WEBSOCKET MESSAGE
// ==================================================

websocket.onmessage =
    function (event) {

        console.log(
            "WebSocket сообщение:",
            event.data
        );


        try {

            var data =
                JSON.parse(
                    event.data
                );


            // ==================================================
            // НОВАЯ РЫБКА
            // ==================================================

            if (
                data.type ===
                    "new_fish" &&
                data.url
            ) {

                console.log(
                    "Новая рыбка получена:",
                    data.url
                );


                addFishFromUrl(

                    data.url,

                    data.direction,

                    data.confidence,

                    data.fish_id

                );

            }


            // ==================================================
            // УДАЛЕНИЕ РЫБКИ
            // ==================================================

            if (
                data.type ===
                    "remove_fish" &&
                data.fish_id
            ) {

                console.log(
                    "Получена команда удаления рыбки:",
                    data.fish_id
                );


                removeFishById(
                    data.fish_id
                );

            }

        } catch (error) {

            console.error(
                "Ошибка обработки WebSocket сообщения:",
                error
            );

        }

    };


// ==================================================
// WEBSOCKET ERROR
// ==================================================

websocket.onerror =
    function (error) {

        console.error(
            "WebSocket ошибка:",
            error
        );

    };


// ==================================================
// WEBSOCKET CLOSE
// ==================================================

websocket.onclose =
    function () {

        console.log(
            "WebSocket отключён."
        );

    };


// ==================================================
// РЕГИСТРАЦИЯ УСТРОЙСТВА
// ==================================================

function registerScreenDevice() {

    console.log(
        "Получаем конфигурацию устройства..."
    );


    return fetch(
        "/api/device/config"
    )

        .then(
            function (configResponse) {

                console.log(
                    "Device config status:",
                    configResponse.status
                );


                if (
                    !configResponse.ok
                ) {

                    throw new Error(
                        "Не удалось получить конфигурацию устройства."
                    );

                }


                return configResponse.json();

            }
        )

        .then(
            function (config) {

                console.log(
                    "Код устройства:",
                    config.device_code
                );


                // ==================================================
                // РЕГИСТРАЦИЯ
                // ==================================================

                return fetch(

                    "/api/device/register",

                    {

                        method:
                            "POST",

                        headers:
                            {
                                "Content-Type":
                                    "application/json"
                            },

                        body:
                            JSON.stringify({

                                device_code:
                                    config.device_code

                            })

                    }

                );

            }
        )

        .then(
            function (registerResponse) {

                console.log(
                    "Device register status:",
                    registerResponse.status
                );


                if (
                    !registerResponse.ok
                ) {

                    throw new Error(
                        "Устройство не зарегистрировано."
                    );

                }


                return registerResponse.json();

            }
        )

        .then(
            function (result) {

                console.log(
                    "Устройство зарегистрировано:",
                    result
                );


                if (
                    !result.device
                ) {

                    throw new Error(
                        "Сервер не вернул данные устройства."
                    );

                }


                deviceSiteId =
                    result.device.site_id;


                console.log(
                    "ID площадки устройства:",
                    deviceSiteId
                );


                console.log(
                    "Площадка:",
                    result.device.site_id
                );


                console.log(
                    "Устройство:",
                    result.device.name
                );

            }
        )

        .catch(
            function (error) {

                console.error(
                    "Ошибка регистрации устройства:",
                    error
                );

            }
        );
}


// ==================================================
// ЗАПУСК ЭКРАНА
// ==================================================

function startScreen() {

    console.log(
        "START SCREEN"
    );


    registerScreenDevice()

        .then(
            function () {


                if (
                    deviceSiteId ===
                    null
                ) {

                    console.error(
                        "Экран не может загрузить рыбок: площадка не определена."
                    );


                    return;

                }


                console.log(
                    "Площадка определена. Загружаем рыбок..."
                );


                return loadFishes();

            }
        )

        .catch(
            function (error) {

                console.error(
                    "Ошибка запуска экрана:",
                    error
                );

            }
        );
}


console.log(
    "ДО START SCREEN"
);


startScreen();


console.log(
    "ПОСЛЕ START SCREEN"
);