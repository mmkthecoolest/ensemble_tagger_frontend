import Base from './Base';

const UploadFolderSrcML = () => {
	return (
		<Base title="srcML Annotator" description="Instructions: put all of the source code into a compressed folder of the following formats: " subsection="upload_folder_srcml" file_formats={["zip", "tar.gz"]}/>
	)
}

export default UploadFolderSrcML;