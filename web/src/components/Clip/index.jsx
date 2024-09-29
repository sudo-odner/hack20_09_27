import React, { useEffect, useState } from "react";
import "./index.scss";
import { useNavigate } from "react-router-dom";
import server_url from "../../site";

function TruncateString(text) {

  if (text.length > 10) {
    return (
      <span>{text.substring(0, 10)}...</span>
    );
  } else {
    return (
      <span>{text}</span>
    );
  }
}




function Clip({ clip_id = 0, chooseClip, chosenClip, setLoad}) {
  const [clipData, setClipData] = useState({
    clip_id: "",
    cover: "",
    title: "",
    duration: "",
  });

  useEffect(() => {


    const fetchClipDetail = async () => {
      try {
          const response = await fetch(`http://localhost:8000/api/get_clip_details/${clip_id}`, {
              method: 'GET',
              headers: {
                  'Content-Type': 'application/json',
              },
          });

          if (response.ok) {
              console.log('Success:', response.status);
              let text = await response.text();

              const data = JSON.parse(text);
              data['cover'] =  `data:image/jpeg;base64,${data['cover']}`
              setClipData(data);

          } else {
              console.error(response.statusText);
          }
      } catch (error) {
          console.error('Error fetching projects:', error);
      }
  };


    fetchClipDetail();
  }, [clip_id]);

  return (
    <div className={"clip" + (chosenClip===clip_id ? " chosen" : "")} onClick={()=>{setLoad(true);chooseClip(clip_id)}}>
      <div className="clip-cover">
        <img
          className="clip-cover-img"
          src={clipData.cover}
          alt=""
        />
      </div>
      <div className="clip-details">
        <h3 className="clip-title">{clipData.title ? TruncateString(clipData.title): ""}</h3>
        {clipData.duration? <p className="clip-date">{Math.floor(clipData.duration/1000)} сек</p>:""}
      </div>
    </div>
  );
}

export default Clip;
