import React from 'react'
import HtmlDocumentComponent from '../component/HtmlDocument.jsx'
import {
  handleFetchResult,
  PopinFixed,
  PopinFixedHeader,
  PopinFixedOption,
  PopinFixedContent,
  Timeline,
  NewVersionBtn,
  ArchiveDeleteContent,
  SelectStatus
} from 'tracim_lib'
import { MODE, debug } from '../helper.js'
import {
  getHtmlDocContent,
  getHtmlDocComment,
  getHtmlDocRevision,
  postHtmlDocNewComment,
  putHtmlDocContent,
  putHtmlDocStatus
} from '../action.async.js'
import i18n from '../i18n.js'

class HtmlDocument extends React.Component {
  constructor (props) {
    super(props)
    this.state = {
      appName: 'html-documents',
      isVisible: true,
      config: props.data ? props.data.config : debug.config,
      loggedUser: props.data ? props.data.loggedUser : debug.loggedUser,
      content: props.data ? props.data.content : debug.content,
      timeline: props.data ? [] : [], // debug.timeline,
      newComment: '',
      timelineWysiwyg: false,
      mode: MODE.VIEW
    }

    document.addEventListener('appCustomEvent', this.customEventReducer)
  }

  customEventReducer = ({ detail: { type, data } }) => { // action: { type: '', data: {} }
    switch (type) {
      case 'html-documents_showApp':
        this.setState({isVisible: true})
        break
      case 'html-documents_hideApp':
        this.setState({isVisible: false})
        break
      case 'html-documents_reloadContent':
        this.setState(prev => ({content: {...prev.content, ...data}, isVisible: true}))
    }
  }

  componentDidMount () {
    console.log('HtmlDocument did mount')

    this.loadContent()
  }

  componentDidUpdate (prevProps, prevState) {
    const { state } = this

    console.log('HtmlDocument did update', prevState, state)
    if (!prevState.content || !state.content) return

    if (prevState.content.content_id !== state.content.content_id) this.loadContent()

    if (state.mode === MODE.EDIT) wysiwyg('#wysiwygNewVersion', this.handleChangeText)

    if (!prevState.timelineWysiwyg && state.timelineWysiwyg) wysiwyg('#wysiwygTimelineComment', this.handleChangeNewComment)
    else if (prevState.timelineWysiwyg && !state.timelineWysiwyg) tinymce.remove('#wysiwygTimelineComment')
  }

  loadContent = async () => {
    const { content, config } = this.state

    const fetchResultHtmlDocument = getHtmlDocContent(config.apiUrl, content.workspace_id, content.content_id)
    const fetchResultComment = getHtmlDocComment(config.apiUrl, content.workspace_id, content.content_id)
    const fetchResultRevision = getHtmlDocRevision(config.apiUrl, content.workspace_id, content.content_id)

    handleFetchResult(await fetchResultHtmlDocument)
      .then(resHtmlDocument => this.setState({content: resHtmlDocument.body}))
      .catch(e => console.log('Error loading content.', e))

    Promise.all([
      handleFetchResult(await fetchResultComment),
      handleFetchResult(await fetchResultRevision)
    ])
      .then(([resComment, resRevision]) => {
        const resCommentWithProperDate = resComment.body.map(c => ({...c, created: (new Date(c.created)).toLocaleString()}))

        const revisionWithComment = resRevision.body
          .map((r, i) => ({
            ...r,
            created: (new Date(r.created)).toLocaleString(),
            timelineType: 'revision',
            commentList: r.comment_ids.map(ci => ({
              timelineType: 'comment',
              ...resCommentWithProperDate.find(c => c.content_id === ci)
            })),
            number: i + 1
          }))
          .reduce((acc, rev) => [
            ...acc,
            rev,
            ...rev.commentList.map(comment => ({
              ...comment,
              customClass: '',
              loggedUser: this.state.config.loggedUser
            }))
          ], [])

        this.setState({timeline: revisionWithComment})
      })
      .catch(e => {
        console.log('Error loading Timeline.', e)
        this.setState({timeline: []})
      })
  }

  handleClickBtnCloseApp = () => {
    this.setState({ isVisible: false })
    GLOBAL_dispatchEvent({type: 'appClosed', data: {}}) // handled by tracim_front::src/container/WorkspaceContent.jsx
  }

  handleSaveEditTitle = async newTitle => {
    const { config, content } = this.state

    const fetchResultSaveHtmlDoc = putHtmlDocContent(config.apiUrl, content.workspace_id, content.content_id, newTitle, content.raw_content)

    handleFetchResult(await fetchResultSaveHtmlDoc)
      .then(resSave => {
        if (resSave.apiResponse.status === 200) this.loadContent()
        else console.warn('Error saving html-document. Result:', resSave, 'content:', content, 'config:', config)
      })
  }

  handleClickNewVersion = () => this.setState({ mode: MODE.EDIT })

  handleCloseNewVersion = () => {
    tinymce.remove('#wysiwygNewVersion')
    this.setState({ mode: MODE.VIEW })
  }

  handleSaveHtmlDocument = async () => {
    const { content, config } = this.state

    const fetchResultSaveHtmlDoc = putHtmlDocContent(config.apiUrl, content.workspace_id, content.content_id, content.label, content.raw_content)

    handleFetchResult(await fetchResultSaveHtmlDoc)
      .then(resSave => {
        if (resSave.apiResponse.status === 200) {
          this.handleCloseNewVersion()
          this.loadContent()
        } else {
          console.warn('Error saving html-document. Result:', resSave, 'content:', content, 'config:', config)
        }
      })
  }

  handleChangeText = e => {
    const newText = e.target.value // because SyntheticEvent is pooled (react specificity)
    this.setState(prev => ({content: {...prev.content, raw_content: newText}}))
  }

  handleChangeNewComment = e => {
    const newComment = e.target.value
    this.setState({newComment})
  }

  handleClickValidateNewCommentBtn = async () => {
    const { config, content, newComment } = this.state

    const fetchResultSaveNewComment = await postHtmlDocNewComment(config.apiUrl, content.workspace_id, content.content_id, newComment)

    handleFetchResult(await fetchResultSaveNewComment)
      .then(resSave => {
        if (resSave.apiResponse.status === 200) {
          this.setState({newComment: ''})
          if (this.state.timelineWysiwyg) tinymce.get('wysiwygTimelineComment').setContent('')
          this.loadContent()
        } else {
          console.warn('Error saving html-document comment. Result:', resSave, 'content:', content, 'config:', config)
        }
      })
  }

  handleToggleWysiwyg = () => this.setState(prev => ({timelineWysiwyg: !prev.timelineWysiwyg}))

  handleChangeStatus = async newStatus => {
    const { config, content } = this.state

    const fetchResultSaveEditStatus = putHtmlDocStatus(config.apiUrl, content.workspace_id, content.content_id, newStatus)

    handleFetchResult(await fetchResultSaveEditStatus)
      .then(resSave => {
        if (resSave.status !== 204) { // 204 no content so dont take status from resSave.apiResponse.status
          console.warn('Error saving html-document comment. Result:', resSave, 'content:', content, 'config:', config)
        } else {
          this.loadContent()
        }
      })
  }

  handleClickArchive = async () => {
    console.log('archive')
    // const { config, content } = this.state
    //
    // const fetchResultArchive = await fetch(`${config.apiUrl}/workspaces/${content.workspace_id}/contents/${content.content_id}/archive`, {
    //   ...FETCH_CONFIG,
    //   method: 'PUT'
    // })
  }

  handleClickDelete = async () => {
    console.log('delete')
    // const { config, content } = this.state
    // const fetchResultDelete = await fetch(`${config.apiUrl}/workspaces/${content.workspace_id}/contents/${content.content_id}/delete`, {
    //   ...FETCH_CONFIG,
    //   method: 'PUT'
    // })
  }

  handleClickShowRevision = revision => {
    console.log('revision', revision)
    this.setState(prev => ({
      content: {
        ...prev.content,
        label: revision.label,
        raw_content: revision.raw_content,
        number: revision.number,
        status: revision.status
      },
      mode: MODE.REVISION
    }))
  }

  handleClickLastVersion = () => {
    this.loadContent()
    this.setState({mode: MODE.VIEW})
  }

  render () {
    const { isVisible, loggedUser, content, timeline, newComment, timelineWysiwyg, config, mode } = this.state

    if (!isVisible) return null

    return (
      <PopinFixed customClass={`${config.slug}`}>
        <PopinFixedHeader
          customClass={`${config.slug}`}
          faIcon={config.faIcon}
          title={content.label}
          onClickCloseBtn={this.handleClickBtnCloseApp}
          onValidateChangeTitle={this.handleSaveEditTitle}
        />

        <PopinFixedOption customClass={`${config.slug}`} i18n={i18n}>
          <div /* this div in display flex, justify-content space-between */>
            <div className='d-flex'>
              <NewVersionBtn onClickNewVersionBtn={this.handleClickNewVersion} disabled={mode === MODE.REVISION} />

              {mode === MODE.REVISION &&
                <button
                  className='wsContentGeneric__option__menu__lastversion html-documents__lastversionbtn btn btn-default'
                  onClick={this.handleClickLastVersion}
                  style={{backgroundColor: config.hexcolor, color: '#fdfdfd'}}
                >
                  <i className='fa fa-code-fork' />
                  Dernière version
                </button>
              }
            </div>

            <div className='d-flex'>
              <SelectStatus
                selectedStatus={config.availableStatuses.find(s => s.slug === content.status)}
                availableStatus={config.availableStatuses}
                onChangeStatus={this.handleChangeStatus}
                disabled={mode === MODE.REVISION}
              />

              <ArchiveDeleteContent
                onClickArchiveBtn={this.handleClickArchive}
                onClickDeleteBtn={this.handleClickDelete}
                disabled={mode === MODE.REVISION}
              />
            </div>
          </div>
        </PopinFixedOption>

        <PopinFixedContent customClass={`${config.slug}__contentpage`}>
          <HtmlDocumentComponent
            mode={mode}
            wysiwygNewVersion={'wysiwygNewVersion'}
            onClickCloseEditMode={this.handleCloseNewVersion}
            onClickValidateBtn={this.handleSaveHtmlDocument}
            version={content.number}
            lastVersion={timeline.filter(t => t.timelineType === 'revision').length}
            text={content.raw_content}
            onChangeText={this.handleChangeText}
            key={'html-documents'}
          />

          <Timeline
            customClass={`${config.slug}__contentpage`}
            loggedUser={loggedUser}
            timelineData={timeline}
            newComment={newComment}
            disableComment={mode === MODE.REVISION}
            wysiwyg={timelineWysiwyg}
            onChangeNewComment={this.handleChangeNewComment}
            onClickValidateNewCommentBtn={this.handleClickValidateNewCommentBtn}
            onClickWysiwygBtn={this.handleToggleWysiwyg}
            onClickRevisionBtn={this.handleClickShowRevision}
            shouldScrollToBottom={mode !== MODE.REVISION}
          />
        </PopinFixedContent>
      </PopinFixed>
    )
  }
}

export default HtmlDocument
