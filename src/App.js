import React from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Home from './templates/Home';
import UploadFileSrcML from './templates/UploadFileSrcML';
import UploadFolderSrcML from './templates/UploadFolderSrcML';
import AnnotateFile from "./templates/AnnotateFile";
//import './App.css';

function App() {
  // usestate for setting a javascript
  // object for storing and using data
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/upload_file_srcml" element={<UploadFileSrcML />} />
        <Route path="/upload_folder_srcml" element={<UploadFolderSrcML />}/>
        <Route path="/upload_file_annotate" element={<AnnotateFile title="Ensemble Tagger" description="Instructions: please use the following file formats for upload: " subsection="upload_file_annotate" file_formats={["java", "cpp", "c", "h"]}/>}/>

      </Routes>
    </BrowserRouter>
  );
}

export default App;
