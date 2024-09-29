import React, { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import server_url from "../../site";
import SearchIcon from "../../icons/SearchIcon.svg";
import Settings from "../../icons/Settings.svg";
import Clear from "../../icons/Close.svg";
import "./index.scss";
import Clip from "../../components/Clip";
import { SwishSpinner } from "react-spinners-kit";
import VideoEditor from "../../components/VideoEditor";
import JSZip from "jszip";

function capitalizeFirstLetter(string) {
    return string.charAt(0).toUpperCase() + string.slice(1);
}

function Project() {
  // const [searchProp, setSearchProp] = useState("");
  const to = useNavigate();

  const { project_id } = useParams();
  const [activated, setActivated] = useState(-1);
  const [data, setData] = useState("");
  const [start, setStart] = useState(0);
  const [end, setEnd] = useState(null);
  const [clips, setClips] = useState([]);
  const [subtitles, setSubtitles] = useState([]);
  const [chosenClip, chooseClip] = useState(-1);
  const [clip, setClip] = useState("");
  const [load, setLoad] = useState(false);

  function home() {
    to("/");
  }

  const on_save = async (metadata) => {
    const update_clip = async () => {
      console.log(metadata);
      let d = JSON.stringify({"subtitles": JSON.stringify(subtitles), "adhd": Number(metadata.adhd), "subtitle": 1})
      console.log(d)
      try {
        const response = await fetch(
          `http://localhost:8000/api/update_clip/${chosenClip}`,
          {
            method: "POST",
            body: d,
       

          }
        );
        console.log(response.body)
        if (response.ok) {
          console.log("Success:", response.status);
          let text = response.text;

          const data = JSON.parse(text);
          console.log(data);

    //   formData.append("start", metadata.trim_times["start"]);
    //   formData.append("end", metadata.trim_times["end"]);
    //   formData.append("resolution", metadata.resolution);
    //   formData.append("extension", "mp4");

          window.open(
            `http://localhost:8000/api/export_clip/${chosenClip}?resolution=${metadata.resolution}&extension=mp4&start=${metadata.trim_times["start"]}&end=${metadata.trim_times["end"]}`,
            "_blank",
            "noopener,noreferrer"
          );
        } else {
          console.error(response.statusText);
        }
      } catch (error) {
        console.error("Error while updating clip", error);
      }
    };

    console.log(15);
    update_clip();
  };

  function updateSub(value, ind) {
    let data = subtitles;
    data[ind] = value;
    console.log(data);
    setSubtitles(data);
  }

  useEffect(() => {
    const fetchUser = async () => {
      try {
        const response = await fetch(
          `http://localhost:8000/api/get_clips/${project_id}`,
          {
            method: "GET",
            headers: {
              "Content-Type": "application/json",
            },
          }
        );

        if (response.ok) {
          console.log("Success:", response.status);
          let text = await response.text();

          const data = JSON.parse(text);
          setClips(data);
        } else {
          console.error(response.statusText);
        }
      } catch (error) {
        console.error("Error fetching projects:", error);
      }
    };

    fetchUser();

    const loadVideo = async () => {
      try {
        const response = await fetch(
          `http://localhost:8000/api/get_clip/${chosenClip}`,
          {
            method: "GET",
            headers: {
              "Content-Type": "application/json",
            },
          }
        );

        if (response.ok) {
          console.log("Success:", response.status);
          // console.log(response.text())
          let blob = await response.blob();

          var new_zip = new JSZip();
          new_zip.loadAsync(blob).then(async function (zipped) {
            let res = await zipped.file("video.mp4").async("blob");
            let details = await JSON.parse(
              await zipped.file("data.json").async("string")
            );
            console.log(zipped, details);
            setData({
              file: res,
              title: "Название клипа",
              subtitles: details["subtitles"],
              tags: "",
            });
            setLoad(false);
          });

          // const data = JSON.parse(text);
          console.log(data);
          // setData(data);
        } else {
          chooseClip(-1);
          setLoad(false);
          console.error(response.statusText);
        }
      } catch (error) {
        console.error("Error fetching projects:", error);
      }
    };

    if (chosenClip !== -1) {
      loadVideo();
    } else {
      setData("");
    }
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
        {/* <div className="search">
                    <div className="srchBrWrapper">
                        <img src={SearchIcon} alt="" />
                        <input
                            placeholder="Поиск"
                            value={searchProp}
                            onChange={(e) => {
                                setSearchProp(e.target.value);
                            }}
                        />
                        {/* <img src={Settings} className="c" alt="" onClick={()=>{setSettings(!settings)}}/> 
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
                </div> */}
        <div className="clips">
          {clips.map((v) => (
            <Clip
              setLoad={setLoad}
              clip_id={v}
              chooseClip={chooseClip}
              chosenClip={chosenClip}
            />
          ))}
        </div>
      </div>

      {load ? (
        <div className="editor" style={{ margin: "auto" }}>
          <h3>Загружаем клип..</h3>
          <SwishSpinner frontColor="#12cced" backColor="#ED143B" />
        </div>
      ) : data ? (
        [
          <div className="editor">
            <div className="videoeditor">
              {/* <h3>{data.title}</h3> */}
              <VideoEditor
                onSave={on_save}
                start={start}
                end={end}
                setStart={setStart}
                setEnd={setEnd}
                file={data.file}
              />
            </div>
          </div>,
          <div className="settings">
            <h1>{data.title}</h1>
            <h3>Описание:</h3>
            <p className="clip-description">{data.meta}</p>
            <div className="subtitles">
              {data.subtitles.map((v, i) => {
                return activated !== i ? (
                  <div className="input">
                    {Math.floor(v.startTime / 1000 / 60)}:
                    {Math.floor(v.startTime / 1000) -
                      Math.floor(v.startTime / 1000 / 60) * 60}
                    -{Math.floor(v.endTime / 1000 / 60)}:
                    {Math.floor(v.endTime / 1000) -
                      Math.floor(v.endTime / 1000 / 60) * 60}
                    <input
                      value={v.text}
                      onClick={() => {
                        setActivated(i);
                      }}
                    />
                  </div>
                ) : (
                  <div className="input">
                    {Math.floor(v.startTime / 1000 / 60)}:
                    {Math.floor(v.startTime / 1000) -
                      Math.floor(v.startTime / 1000 / 60) * 60}
                    -{Math.floor(v.endTime / 1000 / 60)}:
                    {Math.floor(v.endTime / 1000) -
                      Math.floor(v.endTime / 1000 / 60) * 60}
                    <input
                      placeholder={v.text}
                      onChange={(e) => {
                        updateSub(e.target.value, i);
                      }}
                    />
                  </div>
                );
              })}
            </div>
          </div>,
        ]
      ) : (
        <div className="editor" style={{ margin: "auto" }}>
          <h3>Выберите клип</h3>
        </div>
      )}
    </div>
  );
}

export default Project;
