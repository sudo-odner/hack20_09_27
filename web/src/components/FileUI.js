import React, { useEffect, useState } from "react";
import FileIcon from "../icons/FileIcon";

function getVideoCover(file, seekTo = 0.0) {
  console.log("getting video cover for file: ", file);
  return new Promise((resolve, reject) => {
    // load the file to a video player
    const videoPlayer = document.createElement("video");
    videoPlayer.setAttribute("src", URL.createObjectURL(file));
    videoPlayer.load();
    videoPlayer.addEventListener("error", (ex) => {
      reject("error when loading video file", ex);
    });
    // load metadata of the video to get video duration and dimensions
    videoPlayer.addEventListener("loadedmetadata", () => {
      // seek to user defined timestamp (in seconds) if possible
      if (videoPlayer.duration < seekTo) {
        reject("video is too short.");
        return;
      }
      // delay seeking or else 'seeked' event won't fire on Safari
      setTimeout(() => {
        videoPlayer.currentTime = seekTo;
      }, 200);
      // extract video thumbnail once seeking is complete
      videoPlayer.addEventListener("seeked", () => {
        console.log("video is now paused at %ss.", seekTo);
        // define a canvas to have the same dimension as the video
        const canvas = document.createElement("canvas");
        canvas.width = videoPlayer.videoWidth;
        canvas.height = videoPlayer.videoHeight;
        // draw the video frame to canvas
        const ctx = canvas.getContext("2d");
        ctx.drawImage(videoPlayer, 0, 0, canvas.width, canvas.height);
        // return the canvas image as a blob
        ctx.canvas.toBlob(
          (blob) => {
            resolve(blob);
          },
          "image/jpeg",
          0.75 /* quality */
        );
      });
    });
  });
}

export default function FileUI({ fileRef, file, setFile }) {
  const [fileName, setFileName] = useState("");
  const [fileType, setFileType] = useState("");
  const [im, setIm] = useState("");
  const [change, setChange] = useState(1);
  async function onFileChange(event) {
    setChange(change + 1);
    if (event.target.files && event.target.files[0]) {
      let reader = new FileReader();
      let f = event.target.files[0];
      setFileName(f.name);
      setFileType(f.type.split("/")[0]);
      if (f.type.split("/")[0] !== "image") {
        let ext = f.name.split(".").pop() + " file";
        setFileType(ext);
      }
      // reader.onload = function(e) {
      //   setFileOrig(e.target.result);
      // };
      // setFileOrig(f);
      try {
        // get the frame at 1.5 seconds of the video file
        const cover = await getVideoCover(f, 1.5);
        // print out the result image blob
        console.log(cover);
        setIm(cover);
      } catch (ex) {
        console.log("ERROR: ", ex);
      }
      setFile(f);
    }
  }

  const [fileUI, setFileUI] = useState(
    <div className="uploadbutton" onClick={() => fileRef.current.click()}>
      <FileIcon />
      <div style={{ width: "100%", marginTop: "0.5em", textAlign: "center" }}>
        Загрузите видео{" "}
      </div>
      <input
        accept="video/*"
        ref={fileRef}
        onChange={onFileChange}
        multiple={false}
        type="file"
        hidden
      />
    </div>
  );

  useEffect(() => {
    console.log(im);
    if (file) {
      let alt = "";
      alt = (
        <div className="altimg" onClick={() => fileRef.current.click()}>
          <h3 className="alt">{fileType}</h3>
          <p className="filename">{fileName}</p>
        </div>
      );

      setFileUI(
        <div className="uploaded">
          {im  ? (
            <div className="videocover" >
            <img src={URL.createObjectURL(im)} alt="error" onClick={() => fileRef.current.click()} /></div>
          ) : (
            alt
          )}
          <div className="changebutton">
            <input
              accept="video/*"
              ref={fileRef}
              onChange={onFileChange}
              multiple={false}
              type="file"
              hidden
            />
            <p className="uploadeddesc">Нажмите на обложку для изменения</p>
          </div>
        </div>
      );
    }
  }, [im, fileName, fileType, file, change]);
  return fileUI;
}
