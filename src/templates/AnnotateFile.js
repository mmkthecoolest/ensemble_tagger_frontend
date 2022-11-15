import React, { useRef, useEffect, useState } from 'react';
import beautify from 'xml-beautifier';
import download from 'downloadjs';
//import './XMLRender.css'

import {
	Accordion,
	AccordionBody,
	AccordionHeader,
	AccordionItem,
	Button
} from 'reactstrap';
//import download from 'downloadjs';

const AnnotateFile = (props) => {
	const title = props.title;
	//const subsection = props.subsection;

	const [selectedFile, setSelectedFile] = useState();
	const [[result, fileIsAnnotated], setResult] = useState(["", false]);
	const [open, setOpen] = useState('1');
	const [fileIsSubmitted, setFileIsSubmitted] = useState(false);

	//const downloadIsCalled = useRef(false);

	//this gets called every render
	const useEffectCalls = useRef(0);
	useEffect(() => {
		console.log("Use Effect called: " + useEffectCalls.current);
		useEffectCalls.current += 1;
		document.title = title;
	});

	//function used to assign file to UI
	const changeHandler = (event) => {
		setSelectedFile(event.target.files[0]);
		console.log("Invoked changeHandler");
	};

	const handleSubmission = (subsection) => {
		if (selectedFile !== undefined) {
			const formData = new FormData();
			const filename = selectedFile['name'];
			let fileIsValid = false;
			//let fileExtension;
			for (let fileType of props.file_formats) {
				if (filename.endsWith("." + fileType)) {
					fileIsValid = true;
					//fileExtension = "." + fileType;
					break;
				}
			}
			if (fileIsValid) {
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

				setFileIsSubmitted(true);
			} else {
				alert("ERROR: Invalid file format used");
			}
		} else {
			alert("ERROR: Please select a file first");
		}
	};

	const hiddenFileInput = React.useRef(null);
	const handleCustomUploadButtonClick = event => {
		hiddenFileInput.current.click();
	};

	const fileExtensionsString = (fileExtensionsList) => {
		return fileExtensionsList.slice(0, fileExtensionsList.length - 1).join(", ") + " or " + fileExtensionsList.at(-1);
	}

	const fileExtensionsHTML = (fileExtensionsList) => {
		return fileExtensionsList.map((extension) => "." + extension).join(",");
	}

	const toggle = (id) => {
		if (open === id) {
			setOpen();
		} else {
			setOpen(id);
		}
	};


	if (!fileIsAnnotated && !fileIsSubmitted) {
		return (<div className="menu-page">
			<form action="/">
				<input type="submit" value="🏠 Home" className="upload-button"/>
			</form>
			<h1>Choose File</h1>
			<p>{props.description} {fileExtensionsString(props.file_formats)}</p>

			<Button onClick={handleCustomUploadButtonClick} className="upload-button">
        		📁 File Select
      		</Button>
			<span className="uploaded-file-text">{selectedFile !== undefined ? "Selected file: " + selectedFile['name']: 'File not selected'}</span>

			<input type="file" name="file" onChange={changeHandler} accept={fileExtensionsHTML(props.file_formats)} style={{display:'none'}} ref={hiddenFileInput}/>
			<div className="home-buttons-flexbox">
			{Object.keys(props.buttonList).map(key => {
				return <Button onClick={() => handleSubmission(props.buttonList[key])} className="custom-button">{key}</Button>;
			})}
			</div>
		</div>)
	} if (!fileIsAnnotated) {
		return (<div className="menu-page">
			<h1>Please Wait...</h1>
		</div>)
	} else {
		const xmlContent = beautify(result);
		console.log("Beautify result: " + result);

		let trimmedString = xmlContent.substring(xmlContent.indexOf(">")).replace(/>/, "");
		console.log("trimmedString: " + trimmedString);

		let finalString = trimmedString.substring(trimmedString.indexOf("<"));
		console.log("finalString: " + finalString);

		//if(!downloadIsCalled.current){
		//console.log("Download called");
		//download(finalString, (selectedFile['name'] + ".xml"));

		//downloadIsCalled.current = !downloadIsCalled.current;
		//}

		const downloadFile = () => {
			download(finalString, (selectedFile['name'] + ".xml"));
		}

		return (<div className="accordion-page">
			<h1>Results</h1>
			<form action={document.URL}>
				<input type="submit" value="Upload Another File" className="custom-button"/>
			</form>
			<Accordion open={open} toggle={toggle} className="accordion accordion-div">
				<AccordionItem className="accordion">
					<AccordionHeader targetId="1"><div>{selectedFile['name']}</div></AccordionHeader><Button onClick={downloadFile} className="accordion-download-button">Download</Button>
					<AccordionBody className="xml" accordionId="1">
						{finalString}
					</AccordionBody>
				</AccordionItem>
			</Accordion>
		</div>);

		//return (<div className="xml">{finalString}</div>);
	}
}

export default AnnotateFile;