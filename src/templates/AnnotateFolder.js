import React, { useRef, useEffect, useState } from 'react';
import beautify from 'xml-beautifier';
import download from 'downloadjs';
import './XMLRender.css'

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

		return <Accordion open={open} toggle={toggle}>
		{Object.keys(units).map(key => {
			return <AccordionItem>
			<AccordionHeader targetId={units.indexOf(units[key])+1}>{getFileNameFromUnit(units[key])}</AccordionHeader>
			<AccordionBody className="xml" accordionId={units.indexOf(units[key])+1}>
			{units[key].outerHTML}
			</AccordionBody>
		</AccordionItem>;
		})}</Accordion>;
	}


	if (!fileIsAnnotated && !fileIsSubmitted) {
		return (<div>
			<form action="/">
				<input type="submit" value="Home" />
			</form>
			<h1>Choose File</h1>
			<p>{props.description} {fileExtensionsString(props.file_formats)}</p>

			<input type="file" name="file" onChange={changeHandler} accept={fileExtensionsHTML(props.file_formats)} />
			{Object.keys(props.buttonList).map(key => {
				return <Button onClick={() => handleSubmission(props.buttonList[key])}>{key}</Button>;
			})}
		</div>)
	} if (!fileIsAnnotated) {
		return (<div>
			<h1>Please Wait...</h1>
		</div>)
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
			console.log("Showing unit tag content: " + xmlTest.getElementsByTagName('unit')[0].innerHTML);

			console.log("Number of units found in first parse: " + xmlTest.getElementsByTagName('unit').length);
			
			let outerHTMLlist = [];
			
			//create a list of outerHTMLs from innerUnits
			for(let step = 0; step < Array.from(xmlTest.getElementsByTagName('unit')).slice(1).length; step++){
				let listItem = Array.from(xmlTest.getElementsByTagName('unit')).slice(1)[step].outerHTML;
				console.log("Unit " + step + " outerHTML: " + listItem);

				outerHTMLlist.push(listItem);
			}
			
			accordions = unitsToAccordions(Array.from(xmlTest.getElementsByTagName('unit')).slice(1));
		}

		//if(!downloadIsCalled.current){
		//console.log("Download called");
		//download(finalString, (selectedFile['name'] + ".xml"));

		//downloadIsCalled.current = !downloadIsCalled.current;
		//}

		const downloadFile = () => {
			download(finalString, (selectedFile['name'] + ".xml"));
		}

		return (<div>
			<form action={document.URL}>
				<input type="submit" value="Upload a File" />
			</form>
			{accordions}
		</div>);

		//return (<div className="xml">{finalString}</div>);
	}
}

export default AnnotateFolder;