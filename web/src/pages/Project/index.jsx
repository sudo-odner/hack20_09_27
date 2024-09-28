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
    const [clip, setClip] = useState("")

    function home() {
        to("/");
    }

    const [clips, setClips] = useState([]);
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

    useEffect(() => {
        const fetchUser = async () => {
            try {
                const response = await fetch(`http://localhost:8000/api/get_clips/${project_id}`, {
                    method: 'GET',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                });

                if (response.ok) {
                    console.log('Success:', response.status);
                    let text = await response.text();

                    const data = JSON.parse(text);
                    setClips(data);

                } else {
                    console.error(response.statusText);
                }
            } catch (error) {
                console.error('Error fetching projects:', error);
            }
        };

        fetchUser();

        const loadVideo = async () => {
          try {
              const response = await fetch(`http://localhost:8000/api/get_clip/${chosenClip}`, {
                  method: 'GET',
                  headers: {
                      'Content-Type': 'application/json',
                  },
              });

              if (response.ok) {
                  console.log('Success:', response.status);
                  let text = await response.text();

                  const data = JSON.parse(text);
                  console.log(data)
                  // setClip(data);

              } else {
                  console.error(response.statusText);
              }
          } catch (error) {
              console.error('Error fetching projects:', error);
          }
      };


        if (chosenClip !== -1) { setData({ title: `Short ${chosenClip}` }); loadVideo()} else { setData("") }
    }, [chosenClip]);

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
                        <Clip clip_id={v} chooseClip={chooseClip} chosenClip={chosenClip} />
                    ))}
                </div>
            </div>

      {data ? [<div className="editor">
        <div className="videoeditor">
          <h3>{data.title}</h3>
          <VideoEditor file={clip}/>
        </div>
      </div>, 
      <div className="settings">
          <h1>Название клипа</h1>
          <h3>Описание:</h3>
          <p className="clip-description">Механизм использования лимита внутридневного кредита в период работы СБП в ночное время, в выходные и праздничные дни разработан и предоставляется банкам-участникам СБП для обеспечения непрерывной работы Системы быстрых платежей.
          </p>
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
      </div></div>] :  <div className="editor" style={{margin:"auto"}}><h3>Выберите клип</h3></div>}
    </div>
  );
}

export default Project;
