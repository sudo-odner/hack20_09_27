import React, { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import server_url from "../../site";
import SearchIcon from "../../icons/SearchIcon.svg";
import Settings from "../../icons/Settings.svg";
import Clear from "../../icons/Close.svg";
import "./index.scss";
import Clip from "../../components/Clip";
import VideoEditor from "../../components/VideoEditor";

function Project() {
  const [searchProp, setSearchProp] = useState("");

  const to = useNavigate();

  const [chosenClip, chooseClip] = useState(-1);

  function home() {
    to("/");
  }

  const clips = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13];
  const [subtitles, setSubtitles] = useState([
    "So let's say at first I'm like, hey, get the fuck off.",
    "And then we go outside and they go, you don't fucking do it.",
    "And I go, I've been overtly, I've been aggressive.",
    "I've been the big man.",
    "I'm like, look, get the fuck away from me.",
    "And they come out and they want to fight me anyway.",
    "I'll change my body language completely.",
    "I'll say, okay, okay, we're going to fight now, okay.",
    "And then they'll be like, oh, we're going to fight now.",
    "I've tried to tell you not to and you want to fight.",
    "So I've tried to be reasonable.",
    "It's done.",
    "So we're going to fight now.",
    "So let's go.",
    "And I'll start walking towards them.",
  ]);

  const { project_id } = useParams();

  function updateSub(value, ind) {
    let data = subtitles;
    data[ind] = value;
    console.log(data);
    setSubtitles(data);
  }

  const [activated, setActivated] = useState(-1);

  const [data, setData] = useState("");

  useEffect(() => {if (chosenClip!== -1) {setData({title: `Short ${chosenClip}`})} else {setData("")}}, [chosenClip]);

  return (
    <div className="project">
      <div className="sidebar">
        <div className="backbutton">
          <div
            onClick={() => {
              home();
            }}
            className="backbutton-wrapper"
          >
            Все проекты
          </div>
        </div>
        <div className="search">
          <div className="srchBrWrapper">
            <img src={SearchIcon} alt="" />
            <input
              placeholder="Поиск"
              value={searchProp}
              onChange={(e) => {
                setSearchProp(e.target.value);
              }}
            />
            {/* <img src={Settings} className="c" alt="" onClick={()=>{setSettings(!settings)}}/> */}
            {searchProp ? (
              <img
                alt=""
                src={Clear}
                className="c"
                onClick={() => {
                  setSearchProp("");
                }}
              />
            ) : (
              ""
            )}
          </div>
        </div>
        <div className="clips">
          {clips.map((v) => (
            <Clip clip_id={v} chooseClip={chooseClip} chosenClip={chosenClip}/>
          ))}
        </div>
      </div>

      {data ? [<div className="editor">
        <div className="videoeditor">
          <h3>{data.title}</h3>
          <VideoEditor />
        </div>
      </div>,
      <div className="subtitles">
        {subtitles.map((v, i) => {
          return activated !== i ? (
            <div className="input">
              00:01-00:10
              <input
                value={v}
                onClick={() => {
                  setActivated(i);
                }}
              />
            </div>
          ) : (
            <div className="input">
              00:01-00:10
              <input
                placeholder={v}
                onChange={(e) => {
                  updateSub(e.target.value, i);
                }}
              />
            </div>
          );
        })}
      </div>] :  <div className="editor" style={{margin:"auto"}}><h3>Выберите клип</h3></div>}
    </div>
  );
}

export default Project;
