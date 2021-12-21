--SCL - Camera Trap - Duplicate Location and Year (Coordinate)

;
WITH CTDuplicate As
(
SELECT
	CI_CameraTrapDeployment.Longitude
	,CI_CameraTrapDeployment.Latitude
	,YEAR(CI_CameraTrapObservation.ObservationDateTime) AS [Year]

FROM
	CI_CameraTrapObservation
	INNER JOIN CI_CameraTrapDeployment ON (CI_CameraTrapObservation.CI_CameraTrapDeploymentID=CI_CameraTrapDeployment.CI_CameraTrapDeploymentID)
	INNER JOIN CI_UploadedFile ON (CI_CameraTrapObservation.CI_UploadedFileID=CI_UploadedFile.CI_UploadedFileID)
WHERE
	CI_CameraTrapDeployment.Archive=0
	AND CI_CameraTrapObservation.Archive=0
	AND CI_UploadedFile.CI_ScenarioID IS NULL

GROUP BY
	CI_CameraTrapDeployment.Longitude
	,CI_CameraTrapDeployment.Latitude
	,YEAR(CI_CameraTrapObservation.ObservationDateTime)

HAVING COUNT(DISTINCT CI_CameraTrapObservation.CI_CameraTrapObservationID)>1
)

SELECT
	YEAR(CI_CameraTrapObservation.ObservationDateTime) AS [Year]
	,CI_CameraTrapDeployment.Latitude
	,CI_CameraTrapDeployment.Longitude
	,CI_CameraTrapDeployment.Reference
	,CI_CameraTrapDeployment.*
	,CI_CameraTrapObservation.*

FROM
	CI_CameraTrapObservation
	INNER JOIN CI_CameraTrapDeployment ON (CI_CameraTrapObservation.CI_CameraTrapDeploymentID=CI_CameraTrapDeployment.CI_CameraTrapDeploymentID)
	INNER JOIN CTDuplicate ON
	(
		CI_CameraTrapDeployment.Latitude=CTDuplicate.Latitude
		AND
		CI_CameraTrapDeployment.Longitude=CTDuplicate.Longitude
		AND
		YEAR(CI_CameraTrapObservation.ObservationDateTime)=CTDuplicate.[Year]
	)
	INNER JOIN CI_UploadedFile ON (CI_CameraTrapObservation.CI_UploadedFileID=CI_UploadedFile.CI_UploadedFileID)

WHERE
	CI_CameraTrapDeployment.Archive=0
	AND CI_CameraTrapObservation.Archive=0
	AND CI_UploadedFile.CI_ScenarioID IS NULL
	
ORDER BY 1,2,3