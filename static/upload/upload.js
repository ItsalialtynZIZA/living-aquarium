const cameraInput = document.getElementById("camera-input");

const previewSection =
    document.getElementById("preview-section");

const previewImage =
    document.getElementById("preview-image");

const retakeButton =
    document.getElementById("retake-button");

const continueButton =
    document.getElementById("continue-button");

const submitButton =
    document.getElementById("submit-button");

const successSection =
    document.getElementById("success-section");


// ==================================================
// СОСТОЯНИЕ
// ==================================================

let selectedFile = null;

let isMirrored = false;

let currentObjectUrl = null;

let previewObjectUrl = null;

let previewReady = false;

let isProcessing = false;


// ==================================================
// КНОПКА ОТЗЕРКАЛИВАНИЯ
// ==================================================

const mirrorButton =
    document.createElement("button");

mirrorButton.type = "button";

mirrorButton.id =
    "mirror-button";

mirrorButton.className =
    "rotation-button";

mirrorButton.textContent =
    "Отразить ↔";

retakeButton.parentNode.insertBefore(
    mirrorButton,
    retakeButton
);


// ==================================================
// ФОТОГРАФИЯ
// ==================================================

cameraInput.addEventListener(
    "change",
    function () {

        const file =
            cameraInput.files[0];

        if (!file) {
            return;
        }

        selectedFile = file;

        isMirrored = false;

        previewReady = false;

        isProcessing = false;


        // Освобождаем старый URL

        if (currentObjectUrl) {

            URL.revokeObjectURL(
                currentObjectUrl
            );

            currentObjectUrl = null;
        }


        // Освобождаем старый preview

        if (previewObjectUrl) {

            URL.revokeObjectURL(
                previewObjectUrl
            );

            previewObjectUrl = null;
        }


        // Создаём URL фотографии

        currentObjectUrl =
            URL.createObjectURL(file);


        previewImage.src =
            currentObjectUrl;


        previewImage.style.transform =
            "scaleX(1)";


        previewSection.classList.remove(
            "hidden"
        );

        successSection.classList.add(
            "hidden"
        );


        // На первом этапе показываем
        // только фотографию

        continueButton.classList.remove(
            "hidden"
        );

        submitButton.classList.add(
            "hidden"
        );

        continueButton.disabled =
            false;

        continueButton.textContent =
            "Продолжить →";


        console.log(
            "Фотография выбрана:",
            file.name
        );

    }
);


// ==================================================
// ОТЗЕРКАЛИВАНИЕ
// ==================================================

mirrorButton.addEventListener(
    "click",
    function () {

        if (!selectedFile) {
            return;
        }

        // Во время обработки ничего
        // менять нельзя

        if (isProcessing) {
            return;
        }


        isMirrored =
            !isMirrored;


        updatePreview();


        console.log(
            "Зеркальное отражение:",
            isMirrored
        );

    }
);


// ==================================================
// ОБНОВЛЕНИЕ ФОТО
// ==================================================

function updatePreview() {

    if (isMirrored) {

        previewImage.style.transform =
            "scaleX(-1)";

    } else {

        previewImage.style.transform =
            "scaleX(1)";
    }
}


// ==================================================
// СОЗДАНИЕ ОТЗЕРКАЛЕННОГО ФАЙЛА
// ==================================================

async function createMirroredFile(file) {

    if (!isMirrored) {
        return file;
    }


    return new Promise(
        (resolve, reject) => {

            const image =
                new Image();

            const objectUrl =
                URL.createObjectURL(file);


            image.onload =
                function () {

                    try {

                        const canvas =
                            document.createElement(
                                "canvas"
                            );


                        canvas.width =
                            image.width;

                        canvas.height =
                            image.height;


                        const context =
                            canvas.getContext(
                                "2d"
                            );


                        if (!context) {

                            throw new Error(
                                "Не удалось создать Canvas."
                            );

                        }


                        context.translate(
                            image.width,
                            0
                        );


                        context.scale(
                            -1,
                            1
                        );


                        context.drawImage(
                            image,
                            0,
                            0
                        );


                        canvas.toBlob(
                            function (blob) {

                                if (!blob) {

                                    reject(
                                        new Error(
                                            "Не удалось создать зеркальное изображение."
                                        )
                                    );

                                    return;
                                }


                                const mirroredFile =
                                    new File(
                                        [blob],
                                        "drawing_mirrored.jpg",
                                        {
                                            type:
                                                "image/jpeg",

                                            lastModified:
                                                Date.now()
                                        }
                                    );


                                resolve(
                                    mirroredFile
                                );

                            },
                            "image/jpeg",
                            0.95
                        );


                    } catch (error) {

                        reject(error);

                    } finally {

                        URL.revokeObjectURL(
                            objectUrl
                        );

                    }

                };


            image.onerror =
                function () {

                    URL.revokeObjectURL(
                        objectUrl
                    );

                    reject(
                        new Error(
                            "Не удалось прочитать изображение."
                        )
                    );

                };


            image.src =
                objectUrl;

        }
    );
}


// ==================================================
// ПРОДОЛЖИТЬ → OPEN-CV
// ==================================================

continueButton.addEventListener(
    "click",
    async function () {

        if (!selectedFile) {

            alert(
                "Сначала сделайте фотографию."
            );

            return;
        }


        if (isProcessing) {
            return;
        }


        await createPreview();

    }
);


// ==================================================
// PREVIEW OPEN-CV
// ==================================================

async function createPreview() {

    if (!selectedFile) {
        return;
    }


    isProcessing = true;

    previewReady = false;


    continueButton.disabled =
        true;

    mirrorButton.disabled =
        true;

    retakeButton.disabled =
        true;


    continueButton.textContent =
        "Обрабатываем...";


    try {

        console.log(
            "Создаём OpenCV preview..."
        );


        const fileToPreview =
            await createMirroredFile(
                selectedFile
            );


        const formData =
            new FormData();


        formData.append(
            "file",
            fileToPreview
        );


        const response =
            await fetch(
                "/api/preview",
                {
                    method: "POST",
                    body: formData
                }
            );


        const result =
            await response.json();


        console.log(
            "Ответ preview:",
            result
        );


        if (!response.ok) {

            throw new Error(
                result.detail ||
                "Не удалось обработать рисунок."
            );

        }


        // Освобождаем старый preview

        if (previewObjectUrl) {

            URL.revokeObjectURL(
                previewObjectUrl
            );

        }


        previewObjectUrl =
            result.preview_url;


        // Показываем уже обработанную рыбку

        previewImage.src =
            result.preview_url;


        previewImage.style.transform =
            "scaleX(1)";


        previewReady = true;


        console.log(
            "Preview загружен:",
            result.preview_url
        );


        // ------------------------------------------
        // Переходим ко второму этапу
        // ------------------------------------------

        continueButton.classList.add(
            "hidden"
        );


        submitButton.classList.remove(
            "hidden"
        );


        mirrorButton.classList.add(
            "hidden"
        );


        continueButton.textContent =
            "Продолжить →";


    } catch (error) {

        console.error(
            "Ошибка создания preview:",
            error
        );


        alert(
            "Не удалось обработать рисунок.\n\n" +
            error.message
        );


        continueButton.disabled =
            false;


    } finally {

        isProcessing =
            false;


        mirrorButton.disabled =
            false;


        retakeButton.disabled =
            false;


        if (!previewReady) {

            continueButton.textContent =
                "Продолжить →";

        }

    }

}


// ==================================================
// ПЕРЕСНЯТЬ
// ==================================================

retakeButton.addEventListener(
    "click",
    function () {

        cameraInput.value = "";

        selectedFile = null;

        isMirrored = false;

        previewReady = false;

        isProcessing = false;


        previewImage.src = "";

        previewImage.style.transform =
            "scaleX(1)";


        if (currentObjectUrl) {

            URL.revokeObjectURL(
                currentObjectUrl
            );

            currentObjectUrl = null;
        }


        if (previewObjectUrl) {

            URL.revokeObjectURL(
                previewObjectUrl
            );

            previewObjectUrl = null;
        }


        previewSection.classList.add(
            "hidden"
        );


        successSection.classList.add(
            "hidden"
        );


        continueButton.classList.remove(
            "hidden"
        );


        submitButton.classList.add(
            "hidden"
        );


        mirrorButton.classList.remove(
            "hidden"
        );


        continueButton.disabled =
            false;


        mirrorButton.disabled =
            false;


        retakeButton.disabled =
            false;


        continueButton.textContent =
            "Продолжить →";


        console.log(
            "Фотография сброшена."
        );

    }
);


// ==================================================
// ОТПРАВКА РЫБКИ
// ==================================================

submitButton.addEventListener(
    "click",
    async function () {

        if (!selectedFile) {

            alert(
                "Сначала сделайте фотографию."
            );

            return;
        }


        if (!previewReady) {

            alert(
                "Сначала обработайте рисунок."
            );

            return;
        }


        submitButton.disabled =
            true;


        retakeButton.disabled =
            true;


        submitButton.textContent =
            "Отправляем рыбку...";


        try {

            console.log(
                "Отправляем рисунок..."
            );


            const fileToSend =
                await createMirroredFile(
                    selectedFile
                );


            const formData =
                new FormData();


            formData.append(
                "file",
                fileToSend
            );


            const response =
                await fetch(
                    "/api/upload",
                    {
                        method: "POST",
                        body: formData
                    }
                );


            const result =
                await response.json();


            console.log(
                "Ответ сервера:",
                result
            );


            if (!response.ok) {

                throw new Error(
                    result.detail ||
                    "Ошибка загрузки фотографии."
                );

            }


            previewSection.classList.add(
                "hidden"
            );


            successSection.classList.remove(
                "hidden"
            );


            console.log(
                "Рыбка успешно отправлена."
            );


        } catch (error) {

            console.error(
                "Ошибка отправки:",
                error
            );


            alert(
                "Не удалось отправить рисунок.\n\n" +
                error.message
            );


            submitButton.disabled =
                false;


            retakeButton.disabled =
                false;


            submitButton.textContent =
                "Отправить рыбку";

        }

    }
);

