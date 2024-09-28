import React, { useState, useEffect } from "react";
import "./index.scss";
import { useNavigate } from "react-router-dom";
import server_url from "../../site";
import HomeProject from "../../components/HomeProject";

function Home() {
    const to = useNavigate();
    const [projects, setProjects] = useState([]);
    const [errorMes, setErrorMes] = useState("");

    useEffect(() => {
        const fetchProjects = async () => {
            try {
                const response = await fetch('http://localhost:8000/api/get_projects', {
                    method: 'GET',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                });

                if (response.ok) {
                    console.log('Success:', response.status);
                    let text = await response.text();

                    const data = JSON.parse(text);
                    setProjects(data);

                } else {
                    console.error(response.statusText);
                }
            } catch (error) {
                console.error('Error fetching projects:', error);
            }
        };

        fetchProjects();
    }, []);



    function create_project() {
        console.log("Creating Project..");
        to("/create");
    }

    return (
        <div className="home">
            <div className="main-container">
                <div className="home-wrapper">
                    <h1 className="home-title"><img width={"225px"} src="/logo.png" />PUTOSHKA</h1>
                    <div className="createbutton">
                        <div
                            onClick={() => {
                                create_project();
                            }}
                            className="createbutton-wrapper"
                        >
                            Новый проект
                        </div>
                        <p className="b4" color="red">
                            {errorMes}
                        </p>
                    </div>
                    <div className="projects">
                        {projects.map((value) => (
                            <HomeProject project_id={value["id"]} img={value["cover"]} title={value["name"]} date={value["datetime"]} />
                        ))}
                    </div>
                </div>
            </div>
        </div>
    );
}

export default Home;
