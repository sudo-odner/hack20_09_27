import React, { useRef, useState, useEffect } from "react";
import "./index.scss";
import { useNavigate } from "react-router-dom";
import server_url from "../../site";
import FileUI from "../../components/FileUI";

function Create({ setCookie, setCookieR }) {
    const to = useNavigate();

    const [title, setTitle] = useState("");
    const fileRef = useRef();
    const [file, setFile] = useState("");
    const [errorMes, setErrorMes] = useState("");
    const [upload, setUpload] = useState(false);
    const [projectId, setProjectId] = useState(0);

    function create_project() {
        const fetchProjects = async () => {
            const formData = new FormData();
            formData.append('name', title);
            formData.append('file', file);
            try {
                const response = await fetch('http://localhost:8000/api/create_project', {
                    method: 'POST',
                    body: formData,
                });

                if (response.ok) {
                    console.log('Success:', response.status);
                    let text = await response.text();

                    const data = JSON.parse(text);

                    setProjectId(data["project_id"]);

                } else {
                    console.error(response.statusText);
                }
            } catch (error) {
                console.error('Error fetching projects:', error);
            }
        };

        fetchProjects();
    }

    function upload_project() {
        setUpload(true);

        create_project();
    }

    useEffect(() => {
        if (upload && projectId) {
            to(`/project/${projectId}`);
        }
    }, [upload, projectId]);

    function home() {
        to("/")
    }

    let load_view = <div className="create-wrapper"><h1 className="h1">Новый проект</h1>
        <div className="create-field">
            <p>Генерируем виральные моменты..</p>
            <div className="createbutton">
                <div
                    onClick={() => {
                        home();
                    }}
                    className="createbutton-wrapper"
                >
                    Все проекты
                </div>
                <p className="b4" color="red">
                    {errorMes}
                </p>
            </div>
        </div></div>




    return <div className="create">
        <div className="main-container">{
            !upload ?
                <div className="create-wrapper">
                    <h1 className="h1">Новый проект</h1>
                    <div className="create-field">
                        <FileUI fileRef={fileRef} file={file} setFile={setFile} />
                        <div className="input">
                            Название проекта
                            <input
                                className=""
                                onChange={(e) => {
                                    setTitle(e.target.value);
                                }}
                                placeholder="Проект N"
                            />
                        </div>
                        <div className="createbutton">
                            <div
                                onClick={() => {
                                    upload_project();
                                }}
                                className="createbutton-wrapper"
                            >
                                Создать
                            </div>
                            <p className="b4" color="red">
                                {errorMes}
                            </p>
                        </div>
                    </div>
                </div> : load_view}
        </div>
    </div>;
}

export default Create;
