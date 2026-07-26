// ========================================
// UPLOAD PDF
// ========================================

async function uploadPDF() {

    const fileInput =
        document.getElementById("pdfFile");

    const file =
        fileInput.files[0];

    if (!file) {

        alert("Please select a PDF file.");

        return;

    }

    const formData =
        new FormData();

    formData.append("file", file);

    try {

        const response =
            await fetch("/upload", {

                method: "POST",

                body: formData

            });

        const data =
            await response.json();

        document.getElementById(
            "uploadMessage"
        ).innerText =
            data.message || data.error;

        // Reload documents after successful upload

        if (response.ok) {

            loadDocuments();

        }

    } catch (error) {

        console.error(
            "Upload error:",
            error
        );

        alert(
            "Something went wrong while uploading."
        );

    }

}


// ========================================
// LOAD DOCUMENTS
// ========================================

async function loadDocuments() {

    try {

        const response =
            await fetch("/documents");

        const documents =
            await response.json();

        console.log(
            "Documents received:",
            documents
        );

        const select =
            document.getElementById(
                "documentSelect"
            );

        const documentList =
            document.getElementById(
                "documentList"
            );

        const totalDocuments =
            document.getElementById(
                "totalDocuments"
            );


        // Update document count

        totalDocuments.innerText =
            documents.length;


        // Clear old dropdown options

        select.innerHTML =
            `
            <option value="">
                Select a document
            </option>
            `;


        // Clear old document cards

        documentList.innerHTML = "";


        // If no documents exist

        if (documents.length === 0) {

            documentList.innerHTML = `

                <p class="text-slate-400 text-sm">

                    No documents uploaded yet.

                </p>

            `;

            return;

        }


        // Create document options and cards

        for (const doc of documents) {


            // ========================================
            // DROPDOWN OPTION
            // ========================================

            const option =
                document.createElement(
                    "option"
                );

            option.value =
                doc.id;

            option.textContent =
                doc.filename;

            select.appendChild(
                option
            );


            // ========================================
            // DOCUMENT CARD
            // ========================================

            const card =
                document.createElement(
                    "div"
                );


            card.className = `

                p-4

                rounded-xl

                bg-slate-900

                border

                border-white/10

                transition

                duration-300

                hover:-translate-y-1

                hover:border-indigo-500/50

                hover:bg-white/10

                animate-slide-up

            `;


            card.innerHTML = `

                <div class="flex

                            items-center

                            justify-between

                            gap-3">


                    <!-- DOCUMENT INFORMATION -->

                    <div class="flex

                                items-center

                                gap-3

                                min-w-0">


                        <div class="w-10

                                    h-10

                                    rounded-lg

                                    bg-red-500/10

                                    flex

                                    items-center

                                    justify-center

                                    text-xl">

                            📄

                        </div>


                        <div class="min-w-0">


                            <p class="font-semibold

                                      truncate">

                                ${doc.filename}

                            </p>


                            <p class="text-xs

                                      text-slate-400

                                      mt-1">

                                Uploaded document

                            </p>


                        </div>


                    </div>


                    <!-- ACTION BUTTONS -->

                    <div class="flex gap-2">


                        <!-- SELECT BUTTON -->

                        <button

                            onclick="selectDocument(${doc.id})"

                            class="px-3

                                   py-2

                                   rounded-lg

                                   bg-indigo-600/20

                                   text-indigo-300

                                   text-sm

                                   hover:bg-indigo-600/40

                                   transition">

                            Select

                        </button>


                        <!-- DELETE BUTTON -->

                        <button

                            onclick="deleteDocument(${doc.id})"

                            class="px-3

                                   py-2

                                   rounded-lg

                                   bg-red-600/20

                                   text-red-300

                                   text-sm

                                   hover:bg-red-600/40

                                   transition">

                            🗑️

                        </button>


                    </div>


                </div>

            `;


            documentList.appendChild(
                card
            );

        }


    } catch (error) {

        console.error(

            "Error loading documents:",

            error

        );

        alert(

            "Could not load documents."

        );

    }

}


// ========================================
// SELECT DOCUMENT
// ========================================

function selectDocument(documentId) {


    const select =
        document.getElementById(
            "documentSelect"
        );


    // Select document in dropdown

    select.value =
        documentId;


    // Get selected option

    const selectedOption =
        select.options[
            select.selectedIndex
        ];


    // Update selected document text

    const selectedDocumentText =
        document.getElementById(
            "selectedDocumentText"
        );


    if (selectedDocumentText) {

        selectedDocumentText.innerText =
            "✅ Selected: " +
            selectedOption.textContent;

    }


    console.log(

        "Selected document ID:",

        documentId

    );

}


// ========================================
// DELETE DOCUMENT
// ========================================

async function deleteDocument(documentId) {


    const confirmDelete =
        confirm(

            "Are you sure you want to delete this document?"

        );


    if (!confirmDelete) {

        return;

    }


    try {


        const response =
            await fetch(

                `/documents/${documentId}`,

                {

                    method: "DELETE"

                }

            );


        const data =
            await response.json();


        alert(

            data.message ||

            data.error

        );


        // Reload documents

        loadDocuments();


    } catch (error) {


        console.error(

            "Delete error:",

            error

        );


        alert(

            "Could not delete document."

        );

    }

}


// ========================================
// ASK AI
// ========================================

async function askAI() {


    const question =
        document.getElementById(
            "question"
        ).value;


    const documentId =
        document.getElementById(
            "documentSelect"
        ).value;


    if (question.trim() === "") {


        alert(

            "Please enter a question."

        );


        return;

    }


    if (documentId === "") {


        alert(

            "Please select a document."

        );


        return;

    }


    try {


        const response =
            await fetch(

                "/ask",

                {

                    method: "POST",


                    headers: {

                        "Content-Type":
                            "application/json"

                    },


                    body: JSON.stringify({

                        question:
                            question,


                        document_id:
                            documentId

                    })

                }

            );


        const data =
            await response.json();


        document.getElementById(

            "answer"

        ).innerText =

            data.answer ||

            data.error;


    } catch (error) {


        console.error(

            "Ask AI error:",

            error

        );


        document.getElementById(

            "answer"

        ).innerText =

            "Something went wrong.";

    }

}


// ========================================
// SUMMARIZE DOCUMENT
// ========================================

async function summarizeDocument() {


    const documentId =
        document.getElementById(

            "documentSelect"

        ).value;


    if (documentId === "") {


        alert(

            "Please select a document."

        );


        return;

    }


    try {


        const response =
            await fetch(

                "/summarize",

                {

                    method: "POST",


                    headers: {

                        "Content-Type":
                            "application/json"

                    },


                    body: JSON.stringify({

                        document_id:
                            documentId

                    })

                }

            );


        const data =
            await response.json();


        document.getElementById(

            "summary"

        ).innerText =

            data.summary ||

            data.error;


    } catch (error) {


        console.error(

            "Summary error:",

            error

        );


        document.getElementById(

            "summary"

        ).innerText =

            "Something went wrong.";

    }

}


// ========================================
// LOAD DOCUMENTS WHEN PAGE OPENS
// ========================================

window.onload = function () {

    loadDocuments();

};