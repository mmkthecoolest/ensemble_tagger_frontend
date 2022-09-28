import logo from './logo.svg';
import React, { useState, useEffect } from "react";
import './App.css';

function App() {
  // usestate for setting a javascript
  // object for storing and using data
  const [data, setdata] = useState({
    name: "",
    number: 0,
  });

  // Using useEffect for single rendering
  useEffect(() => {
    // Using fetch to fetch the api from 
    // flask server it will be redirected to proxy
    fetch("/reactjs-test").then((res) =>
      res.json().then((data) => {
        // Setting a data from api
        setdata({
          name: data.Name,
          number: data.Number,
        });
      })
    );
  }, []);

  return (
    <div className="App">
      <header className="App-header">
        <h1>React and flask</h1>
        <p>{data.name}</p>
        <p>{data.number}</p>

      </header>
    </div>
  );
}

export default App;
