import React, { useEffect, useState } from "react";
import { Buffer } from 'buffer';
import "./index.scss";
import { useNavigate } from "react-router-dom";
import server_url from "../../site";

function HomeProject({ project_id = 0, img = "", title = "", date = "" }) {
    const [projectData, setProjectData] = useState({
        project_id: 0,
        img: "",
        title: "",
        date: "",
    });

    const to = useNavigate()

    const load_project_data = (id) => {

        date = Intl.DateTimeFormat('en-US', {year: 'numeric', month: '2-digit',day: '2-digit'} ).format(Date.parse(date))

        return {
            project_id: project_id,
            img: `data:image/jpeg;base64,${img}`,
            title: title,
            date: date,
        };
    };

    useEffect(() => {
        setProjectData(load_project_data(project_id));
    }, [project_id]);

    return (
        <div className="homeproject" onClick={() => { to(`/project/${project_id}`) }}>
            <div className="homeproject-cover">
                <img
                    className="homeproject-cover-img"
                    src={projectData["img"]}
                    alt=""
                />
            </div>
            <div className="homeproject-details">
                <h3 className="homeproject-title">{projectData.title}</h3>
                <p className="homeproject-date">{projectData.date}</p>
            </div>
        </div>
    );
}

export default HomeProject;
