import React, { useEffect, useState } from 'react';
//import download from 'downloadjs';

const AnnotateFile = (props) => {
	const title = props.title;
	const subsection = props.subsection;

	const [selectedFile, setSelectedFile] = useState();
	const [[result, fileIsAnnotated], setResult] = useState(["", false]);

	//function used to assign file to UI
	const changeHandler = (event) => {
		setSelectedFile(event.target.files[0]);
		console.log("Invoked changeHandler");
	};

	const handleSubmission = () => {
		const formData = new FormData();
		const filename = selectedFile['name'];
		let fileIsValid = false;
		//let fileExtension;
		for(let fileType of props.file_formats){
			if (filename.endsWith("." + fileType)){
				fileIsValid = true;
				//fileExtension = "." + fileType;
				break;
			}
		}
		if(fileIsValid){
			formData.append('file', selectedFile);

			fetch(
				'http://localhost:5000/' + subsection,
				{
					method: 'POST',
					/*headers:{
						"access-control-allow-origin" : "*"
					},*/
					body: formData
				}
			)

			.then((response) => {
				return response.text();
				//result = response.json();
				//console.log(result);
			})

			.then((responseText) => {
				setResult([responseText, true]);
			})
		} else {
			alert("ERROR: Invalid file format used");
		}

	};

	useEffect(() => {
		document.title = title;
	});

	const fileExtensionsString = (fileExtensionsList) => {
		return fileExtensionsList.slice(0, fileExtensionsList.length - 1).join(", ") + " or " + fileExtensionsList.at(-1);
	}

	const fileExtensionsHTML = (fileExtensionsList) => {
		return fileExtensionsList.map((extension) => "." + extension).join(",");
	}

	if(!fileIsAnnotated){
	return (<div>
		<form action="/">
			<input type="submit" value="Home" />
		</form>
		<h1>Choose File</h1>
		<p>{props.description} {fileExtensionsString(props.file_formats)}</p>

		<input type="file" name="file" onChange={changeHandler} accept={fileExtensionsHTML(props.file_formats)}/>
		<button onClick={handleSubmission}>Submit</button>
	</div>)
	} else {
		return result;
	}
}

export default AnnotateFile;