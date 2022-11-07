import AnnotateFolder from './AnnotateFolder';

const UploadFolder = () => {
	return (
		<AnnotateFolder title="Upload a File" description="Instructions: please use the following file formats for upload: " file_formats={["zip", "tar.gz"]} buttonList={{ "Annotate Folder with Tagger": "upload_folder_annotate"}} />
	)
}

export default UploadFolder;