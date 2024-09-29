import React, { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

import "./index.scss"; // Импортируем стили для компонента
import Clip from "../../components/Clip"; // Импортируем компонент Clip
import { SwishSpinner } from "react-spinners-kit"; // Импортируем компонент спиннера
import VideoEditor from "../../components/VideoEditor"; // Импортируем компонент видеоредактора
import JSZip from "jszip"; // Импортируем библиотеку JSZip для работы с zip-архивами

// Функция для преобразования первой буквы строки в верхний регистр
function capitalizeFirstLetter(string) {
    return string.charAt(0).toUpperCase() + string.slice(1);
}

function Project() {
  // const [searchProp, setSearchProp] = useState(""); // Комментарий удален, так как эта переменная не используется

  const to = useNavigate(); // Сохраняем хук useNavigate для управления навигацией

  const { project_id } = useParams(); // Извлекаем ID проекта из URL-параметра

  // Состояния для хранения данных
  const [activated, setActivated] = useState(-1); // Индекс выбранного клипа
  const [data, setData] = useState(""); // Данные
  const [start, setStart] = useState(0); // Начальное время клипа
  const [end, setEnd] = useState(null); // Конечное время клипа
  const [clips, setClips] = useState([]); // Массив клипов
  const [subtitles, setSubtitles] = useState(); // Массив субтитров
  const [chosenClip, chooseClip] = useState(-1); // Индекс выбранного клипа
  const [clip, setClip] = useState(""); // Данные клипа
  const [load, setLoad] = useState(false); // Флаг загрузки

  function home() {
    to("/"); // Переход на домашнюю страницу
  }

  // Функция сохранения изменений
  const on_save = async (metadata) => {
    const update_clip = async () => {
      // console.log(metadata); // Удален неиспользуемый лог
      let d = JSON.stringify({"subtitles": JSON.stringify(subtitles), "adhd": metadata.sdvg, "subtitle": true}) // Формируем JSON-данные для обновления
      console.log(d) // Вывод данных в консоль
      try {
        const response = await fetch(
          "http://localhost:8000/api/update_clip/${chosenClip}", // Адрес API для обновления клипа
          {
            method: "POST",
            body: d, // Отправляем JSON-данные
            headers: {
              "Content-type": "application/json; charset=UTF-8"
            }
          }
        );
        console.log(response.body) // Вывод тела ответа в консоль
        if (response.ok) {
          console.log("Success:", response.status);
          let text = response.text;
          const data = JSON.parse(text);
          console.log(data);
        } else {
          console.error(response.statusText);
        }
      } catch (error) {
        console.error("Error while updating clip", error);
      }
      window.open(
        `http://localhost:8000/api/export_clip/${chosenClip}?resolution=${metadata.resolution}&extension=mp4&start=${metadata.trim_times["start"]}&end=${metadata.trim_times["end"]}`,
        "_blank",
        "noopener,noreferrer"
      );
    };
    update_clip();
  };


  // Апдейт субтитров
  function updateSub(value, ind) {
    let data = subtitles;
    console.log(subtitles)
    data[ind].text = value;
    setSubtitles(data);
  }

  useEffect(() => {
    // Фетч клипов их информации
    const fetchClips = async () => {
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

    fetchClips();

    // загрузка клипа(видео)
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
            setSubtitles(details["subtitles"])
            setData({
              file: res,
              title: details['title'],
              subtitles: details["subtitles"],
              about: details['about'],
              tags: details['tags'],
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

    // при тапе на клип загружаем
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
              home(); // кнопка назад
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
            <p className="clip-description">{data.about}</p>
            <h3>Тэги:</h3>
            <p className="clip-description">{data.tags}</p>
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
