"""
Copyright 2021 Cognitive Scale, Inc. All Rights Reserved.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
# pylint: disable=line-too-long
PROFILE_SCHEMA_COMMON = """
    name
    title
    names { title categories singular plural}
    description
    primarySource {
        attributes
        name
        profileGroup 
        profileKey
        timestamp {
            auto
            field
            fixed {
                format    
                value
            }
            format
        }     
    }
    joins {
        attributes
        join {
            joinSourceColumn
            primarySourceColumn
        }
        name
        profileGroup
        timestamp {
            auto
            field
            fixed {
                format
                value
            }
            format
        }
    }
    bucketAttributes {
        name
        profileGroup
        source {
            name
        }
        buckets {
            filter
            name
        }
    }
    customAttributes {
        expression
        name
        profileGroup
        source {
            name
        }
        window
    }
"""

PROFILE_SCHEMA_SUMMARY = (
    """query profileSchemaByName($project: String!, $name: String!) {
 profileSchemaByName(project: $project, name: $name) {%s}}"""
    % PROFILE_SCHEMA_COMMON
)

FIND_SCHEMAS = (
    """query profileSchemas($project: String!) {
 profileSchemas(project: $project) {%s}}"""
    % PROFILE_SCHEMA_COMMON
)

FIND_PROFILES = """query ProfileList(
  $attributes: [String!]
  $filter: String
  $limit: Int
  $profileSchema: String!
  $project: String!
) {
  profiles(
    attributes: $attributes
    filter: $filter
    limit: $limit
    profileSchema: $profileSchema
    project: $project
  ) {
    attributes {
      group
      timestamp 
      key
      source
      type
      value
    }
    profileID
    profileSchema
  }
}"""

PROFILES_FOR_PLAN = """
query profilesForPlan(
  $project: String!
  $simulationId: String!
  $profileSchema: String!
  $planId: String!
  $filter: String
  $limit: Int
) {
  profilesForPlan(
    project: $project
    simulationId: $simulationId
    profileSchema: $profileSchema
    planId: $planId
    filter: $filter
    limit: $limit
  ) {
    profileID
    profileSchema
    attributes {
      group
      key
      source
      timestamp
      type
      value
    }
  }
}
"""
PROFILE_BY_ID = """query ProfileViewer($project: String!, $schema: String!, $profile: ID!) {
  profile: profileById(
    project: $project
    profileSchema: $schema
    id: $profile
  ) {
    attributes {
      group
      key
      source
      timestamp
      type
      value
    }
    profileID
    profileSchema
  }
}
"""

PROFILE_GROUP_COUNT = """query ProfileGroupCount($project: String!, $schema: String!, $filter: String,
$groupBy: [String!]!, $limit: Int) {
  profileGroupCount(project: $project, profileSchema: $schema, filter: $filter, groupBy: $groupBy, limit: $limit) {
    key
    count
  }
}
"""

PROFILE_COUNT = """query profileCount($project: String!, $schema: String!, $filter: String) {
    profileCount(project: $project, profileSchema: $schema, filter: $filter)
 }
 """

PROFILE_FEATURES = """query ProfileFeatures($project: String!, $profileSchema: String!) {
  profileFeatures(project: $project, profileSchema: $profileSchema) {
    dataType
    featureName
    featureType
    maxValue
    meanValue
    minValue
    pctDom
    pctNull
    profileGroup
    observations
    stdDev
    uniqueCount
  }
}
"""

PROFILE_HISTORY = """query ProfileHistory($project: String!, $profileSchema: String!, $limit: Int) {
  profileHistory(project: $project, profileSchema: $profileSchema, limit: $limit) {
    profileSchema
    project
    commitInfo{
        clusterId
        isBlindAppend
        isolationLevel
        operation
        operationMetrics
        operationParams
        readVersion
        timestamp
        userId
        userMetadata
        version
    }
  }
}
"""

DELETE_PROFILE_SCHEMA = """
mutation DeleteProfileSchema($input: DeleteProfileSchemaInput!){
    deleteProfileSchema(input: $input)
}
"""

DELETE_PROFILES = """
mutation DeleteProfiles($project: String!, $profileSchema: String!, $filter: String!){
    deleteProfiles(project: $project, profileSchema: $profileSchema, filter: $filter){
    endTime
    errorMessage
    isActive
    isCancelled
    isComplete
    isError
    jobId
    jobType
    project
    resourceName
    resourceType
    startTime
    }
}
"""

DELETE_ALL_PROFILES = """
mutation DeleteAllProfiles($project: String!, $profileSchema: String!){
    deleteAllProfiles(project: $project, profileSchema: $profileSchema){
    endTime
    errorMessage
    isActive
    isCancelled
    isComplete
    isError
    jobId
    jobType
    project
    resourceName
    resourceType
    startTime
    }
}
"""

CREATE_PROFILE_SCHEMA = (
    """
mutation CreateProfileSchema($input: ProfileSchemaInput!) {
  createProfileSchema(input: $input) {
    %s
  }
}
"""
    % PROFILE_SCHEMA_COMMON
)

UPDATE_PROFILE_SCHEMA = (
    """
mutation UpdateProfileSchema($input: ProfileSchemaInput!) {
  updateProfileSchema(input: $input) {
    %s
  }
}
"""
    % PROFILE_SCHEMA_COMMON
)

CREATE_BUCKET_ATTRIBUTE = (
    """
mutation CreateBucketAttribute($input: CreateBucketAttributeInput!) {
  createBucketAttribute(input: $input){%s}
}
"""
    % PROFILE_SCHEMA_COMMON
)

CREATE_CUSTOM_ATTRIBUTE = (
    """
mutation CreateCustomAttribute($input: CreateCustomAttributeInput!) {
  createCustomAttribute(input: $input) {
    %s
  }
}
"""
    % PROFILE_SCHEMA_COMMON
)

BUILD_PROFILES_FROM_SCHEMA = """
mutation BuildProfiles($project: String!, $profileSchema: String!){
  buildProfile(project: $project, profileSchema: $profileSchema){
    endTime
    errorMessage
    isActive
    isCancelled
    isComplete
    isError
    jobId
    jobType
    project
    resourceName
    resourceType
    startTime
  }
}
"""
UPDATE_BUCKET_ATTRIBUTE = (
    """
mutation UpdateBucketAttribute($input: UpdateBucketAttributeInput!) {
  updateBucketAttribute(input: $input){%s}
}
"""
    % PROFILE_SCHEMA_COMMON
)

UPDATE_CUSTOM_ATTRIBUTE = (
    """
mutation UpdateCustomAttribute($input: UpdateCustomAttributeInput!) {
  updateCustomAttribute(input: $input) {
    %s
  }
}
"""
    % PROFILE_SCHEMA_COMMON
)

UPDATE_PROFILES = """
mutation UpdateProfiles($project: String!, $profileSchema: String!, $profiles:[String!]!){
  updateProfiles(project: $project, profileSchema: $profileSchema, profiles: $profiles){
    endTime
    errorMessage
    isActive
    isCancelled
    isComplete
    isError
    jobId
    jobType
    project
    resourceName
    resourceType
    startTime
  }
}
"""

DELETE_BUCKET_ATTRIBUTE = (
    """
mutation DeleteBucketAttribute($input: DeleteBucketAttributeInput!) {
  deleteBucketAttribute(input: $input){%s}
}
"""
    % PROFILE_SCHEMA_COMMON
)

DELETE_CUSTOM_ATTRIBUTE = (
    """
mutation DeleteCustomAttribute($input: DeleteCustomAttributeInput!) {
  deleteCustomAttribute(input: $input) {
    %s
  }
}
"""
    % PROFILE_SCHEMA_COMMON
)

# pylint: enable=line-too-long
