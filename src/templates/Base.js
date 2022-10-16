import React, { useEffect, useState } from 'react';
import download from 'downloadjs';

const Base = (props) => {
	const title = props.title;
	const subsection = props.subsection;

	const [selectedFile, setSelectedFile] = useState();

	//function used to assign file to UI
	const changeHandler = (event) => {
		setSelectedFile(event.target.files[0]);
		console.log("Invoked changeHandler");
	};

	const handleSubmission = () => {
		const formData = new FormData();
		const filename = selectedFile['name'];
		let fileIsValid = false;
		let fileExtension;
		for(let fileType of props.file_formats){
			if (filename.endsWith("." + fileType)){
				fileIsValid = true;
				fileExtension = "." + fileType;
				break;
			}
		}
		if(fileIsValid){
			formData.append('file', selectedFile);
			//var result;

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
				return response.blob()
				//result = response.json();
				//console.log(result);
			})
			
			.then((responseBlob) => {
				download(responseBlob, filename.replace(new RegExp("(\\" + fileExtension + "$)"), ""))
			});
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

	return (<div>
		<form action="/">
			<input type="submit" value="Home" />
		</form>
		<h1>Choose File</h1>
		<p>{props.description} {fileExtensionsString(props.file_formats)}</p>

		<input type="file" name="file" onChange={changeHandler} accept={fileExtensionsHTML(props.file_formats)}/>
		<button onClick={handleSubmission}>Submit</button>
	</div>)
}

export default Base;