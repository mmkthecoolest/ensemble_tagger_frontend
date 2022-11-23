import React, { useRef, useEffect, useState } from 'react';
import beautify from 'xml-beautifier';
import download from 'downloadjs';
import { FileUploader } from "react-drag-drop-files";
//import './XMLRender.css'

import {
	Accordion,
	AccordionBody,
	AccordionHeader,
	AccordionItem,
	Button
} from 'reactstrap';
//import download from 'downloadjs';

const AnnotateFolder = (props) => {
	const title = props.title;
	//const subsection = props.subsection;

	const [selectedFile, setSelectedFile] = useState();
	const [[result, fileIsAnnotated], setResult] = useState(["", false]);
	const [open, setOpen] = useState('1');
	const [fileIsSubmitted, setFileIsSubmitted] = useState(false);
	const [downloadRequest, setDownloadRequest] = useState();
	const [isDownloadReady, setIsDownloadReady] = useState(true);
	const [isFolderEmpty, setIsFolderEmpty] = useState(false);

	//this gets called every render
	const useEffectCalls = useRef(0);
	useEffect(() => {
		console.log("Use Effect called: " + useEffectCalls.current);
		useEffectCalls.current += 1;
		document.title = title;
	});

	//function used to assign file to UI
	const dragNDropChangeHandler = (file) => {
		setSelectedFile(file);
		console.log("Invoked dragNDropChangeHandler");
	}

	const handleSubmission = (requestsToCall) => {
		if (selectedFile !== undefined) {
			const formData = new FormData();
			const filename = selectedFile['name'];
			let fileIsValid = false;
			setDownloadRequest(requestsToCall[1]);
			console.log("Download request subsection: " + downloadRequest);
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
				setFileIsSubmitted(true);
				fetch(
					'http://localhost:5000/' + requestsToCall[0],
					{
						method: 'POST',
						/*headers:{
							"access-control-allow-origin" : "*"
						},*/
						body: formData
					})

					.then((response) => {
						
						return response.text();
						//result = response.json();
						//console.log(result);
					})

					.then((responseText) => {
						//console.log("Response Text: " + responseText);

						if (responseText !== "EMPTY_FOLDER_ERROR"){
							setResult([responseText, true]);
						} else {
							setIsFolderEmpty(true);
							setFileIsSubmitted(false);
							setSelectedFile(undefined);
						}
					})
			} else {
				alert("ERROR: Invalid file format used");
			}
		} else {
			alert("ERROR: Please select a file first");
		}
	};

	const handleDownload = () => {
		if (selectedFile !== undefined) {
			const formData = new FormData();
			const filename = selectedFile['name'];
			let fileIsValid = false;
			let fileExtension;
			console.log("Download request subsection: " + downloadRequest);
			for (let fileType of props.file_formats) {
				if (filename.endsWith("." + fileType)) {
					fileIsValid = true;
					fileExtension = "." + fileType;
					break;
				}
			}
			if (fileIsValid) {
				formData.append('file', selectedFile);
				setIsDownloadReady(false);

				fetch(
					'http://localhost:5000/' + downloadRequest,
					{
						method: 'POST',
						/*headers:{
							"access-control-allow-origin" : "*"
						},*/
						body: formData
					}
				)

				.then((response) => {
					return response.blob();
					//result = response.json();
					//console.log(result);
				})

				.then((responseBlob) => {
					download(responseBlob, filename.replace(new RegExp("(\\" + fileExtension + "$)"), ""));
					setIsDownloadReady(true);
					//setFileIsSubmitted(false)
				});

				//setFileIsSubmitted(true);
			} else {
				alert("ERROR: Invalid file format used");
			}
		} else {
			alert("ERROR: Please select a file first");
		}
	};

	const fileExtensionsString = (fileExtensionsList) => {
		return fileExtensionsList.slice(0, fileExtensionsList.length - 1).join(", ") + " or " + fileExtensionsList.at(-1);
	}

	const toggle = (id) => {
		if (open === id) {
			setOpen();
		} else {
			setOpen(id);
		}
	};

	const stringToXMLDom = (string) => {
		const parser=new DOMParser();
		return parser.parseFromString(string,"text/xml");
	}

	const unitsToAccordions = (units) => {
		//var targetIdNum = 0;
		console.log("Number of units to be generated: " + units.length)

		const getFileNameFromUnit = (unit) => {
			//unitXML = stringToXMLDom(unit);
			let fullFileName = unit.getAttribute("filename");

			return fullFileName.split("/").at(-1);
		}

		return <Accordion open={open} toggle={toggle} className="accordion accordion-div">
		{Object.keys(units).map(key => {
			return <AccordionItem className="accordion">
			<AccordionHeader targetId={(units.indexOf(units[key])+1).toString()}>{getFileNameFromUnit(units[key])}</AccordionHeader>
			<Button onClick={() => download(units[key].outerHTML, getFileNameFromUnit(units[key]) + ".xml")} className="accordion-download-button">Download File</Button>
			<AccordionBody className="xml" accordionId={(units.indexOf(units[key])+1).toString()}>
			{units[key].outerHTML}
			</AccordionBody>
		</AccordionItem>;
		})}</Accordion>;
	}

	if (!fileIsAnnotated && !fileIsSubmitted) {
		return (<div className="menu-page-height">
			<div className="menu-page-align">
				<div className="menu-page">
					<form action="/">
						<input type="submit" value="🏠 Home" className="upload-button" />
					</form>
					<h1>Choose Folder</h1>
					<FileUploader classes="drag-n-dropper" children={<div className='drag-n-dropper-text'>Drag and drop file or click here</div>} handleChange={dragNDropChangeHandler} name="file" types={props.file_formats} hoverTitle=" " />
					{isFolderEmpty ? <p className="empty-folder-warning">Please upload a non-empty compressed folder</p> : ""}
					<p>{props.description} {fileExtensionsString(props.file_formats)}</p>

					{selectedFile !== undefined ? "Selected file: " + selectedFile['name'] : 'File not selected'}


					<div className="home-buttons-flexbox">
						{Object.keys(props.buttonList).map(key => {
							return <Button onClick={() => handleSubmission(props.buttonList[key])} className="custom-button">{key}</Button>;
						})}
					</div>
				</div>
			</div>
		</div>
		)
	} else if (!fileIsAnnotated) {
		return (<div className="menu-page-height">
		<div className="menu-page-align">
				<div className="menu-page">
					<h1>Please Wait...</h1>
				</div>		
			</div>		
		</div>		
		)
	} else {
		const xmlContent = beautify(result);
		console.log("Beautify result: " + result);

		let trimmedString = xmlContent.substring(xmlContent.indexOf(">")).replace(/>/, "");
		console.log("trimmedString: " + trimmedString);

		let finalString = trimmedString.substring(trimmedString.indexOf("<"));
		console.log("finalString: " + finalString);

		const xmlTest = stringToXMLDom(finalString);
		const errorNode = xmlTest.querySelector('parsererror');
		let accordions=null;
		if (errorNode){
			console.log("XML parsing failed");
		} else {
			console.log("XML parsing passed");
			
			accordions = unitsToAccordions(Array.from(xmlTest.getElementsByTagName('unit')).slice(1));
		}

		//if(!downloadIsCalled.current){
		//console.log("Download called");
		//download(finalString, (selectedFile['name'] + ".xml"));

		//downloadIsCalled.current = !downloadIsCalled.current;
		//}

		return (<div className="accordion-page">
			<h1>Results</h1>
			<div className="buttons-flexbox">
			<form action={document.URL}>
				<input type="submit" value="Upload Another Folder" className="custom-button"/>
			</form>
			<Button onClick={handleDownload} disabled={(!isDownloadReady)} className="custom-button">Download Result Archive</Button>
			</div>
			{accordions}
		</div>);

		//return (<div className="xml">{finalString}</div>);
	}
}

export default AnnotateFolder;