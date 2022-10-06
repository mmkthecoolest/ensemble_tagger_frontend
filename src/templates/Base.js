import React, { useEffect } from 'react';

const Base = (props) => {
	const title = props.title;
	useEffect(() => {
		document.title = { title };
	});


	return (<div>
		<h1>Choose File</h1>
		<p>{props.description}</p>

	</div>)
}

export default Base;