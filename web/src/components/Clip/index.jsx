import React, { useEffect, useState } from "react";
import "./index.scss";
import { useNavigate } from "react-router-dom";
import server_url from "../../site";

function Clip({ clip_id = 0, chooseClip, chosenClip}) {
  const [clipData, setClipData] = useState({
    clip_id: "",
    cover: "",
    title: "",
    duration: "",
  });

  const load_clip_data = (id) => {
    return {
      "clip_id": clip_id,
      cover: "https://i.pinimg.com/564x/df/16/82/df16827a9e9888c7cc0988ade16b879c.jpg",
      title: `Short ${clip_id}`,
      duration: "23 sec",
    };
  };

  useEffect(() => {
    setClipData(load_clip_data(clip_id));
  }, [clip_id]);

  return (
    <div className={"clip" + (chosenClip===clip_id ? " chosen" : "")} onClick={()=>{chooseClip(clip_id)}}>
      <div className="clip-cover">
        <img
          className="clip-cover-img"
          src={clipData.cover}
          alt=""
        />
      </div>
      <div className="clip-details">
        <h3 className="clip-title">{clipData.title}</h3>
        <p className="clip-date">{clipData.duration}</p>
      </div>
    </div>
  );
}

export default Clip;
