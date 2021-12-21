--SCL - Ad Hoc - Duplicate Location and Year (Coordinate)

;
WITH AdHocDuplicate As
(
SELECT
	CI_AdHocObservation.Longitude
	,CI_AdHocObservation.Latitude
	,YEAR(CI_AdHocObservation.StartObservationDate) AS [Year]

FROM
	CI_AdHocObservation
	INNER JOIN CI_UploadedFile ON (CI_AdHocObservation.CI_UploadedFileID=CI_UploadedFile.CI_UploadedFileID)

WHERE
	CI_AdHocObservation.Archive=0
	AND CI_UploadedFile.CI_ScenarioID IS NULL

GROUP BY
	CI_AdHocObservation.Longitude
	,CI_AdHocObservation.Latitude
	,YEAR(CI_AdHocObservation.StartObservationDate)

HAVING COUNT(DISTINCT CI_AdHocObservation.CI_AdHocObservationID)>1
)

SELECT
	YEAR(CI_AdHocObservation.StartObservationDate) AS [Year]
	,CI_AdHocObservation.Latitude
	,CI_AdHocObservation.Longitude
	,CI_AdHocObservation.Reference
	,CI_AdHocObservation.*

FROM
	CI_AdHocObservation
	INNER JOIN AdHocDuplicate ON
	(
		CI_AdHocObservation.Latitude=AdHocDuplicate.Latitude
		AND
		CI_AdHocObservation.Longitude=AdHocDuplicate.Longitude
		AND
		YEAR(CI_AdHocObservation.StartObservationDate)=AdHocDuplicate.[Year]
	)
	INNER JOIN CI_UploadedFile ON (CI_AdHocObservation.CI_UploadedFileID=CI_UploadedFile.CI_UploadedFileID)

WHERE
	CI_UploadedFile.CI_ScenarioID IS NULL
	AND CI_AdHocObservation.Archive=0

ORDER BY 1,2,3