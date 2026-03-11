import { ref, onUnmounted } from 'vue'

/**
 * 通用请求Hook
 * @param {Function} requestFn 请求函数
 * @param {Object} options 配置项
 */
export function useRequest(requestFn, options = {}) {
  const {
    immediate = false,
    initialData = null,
    onSuccess = () => {},
    onError = () => {}
  } = options

  const data = ref(initialData)
  const loading = ref(false)
  const error = ref(null)
  const isCanceled = ref(false)

  const run = async (...params) => {
    if (loading.value) return

    loading.value = true
    error.value = null

    try {
      const response = await requestFn(...params)
      if (!isCanceled.value) {
        data.value = response.data
        onSuccess(response.data, response)
      }
      return response
    } catch (err) {
      if (!isCanceled.value) {
        error.value = err
        onError(err)
      }
      throw err
    } finally {
      if (!isCanceled.value) {
        loading.value = false
      }
    }
  }

  const cancel = () => {
    isCanceled.value = true
    loading.value = false
  }

  onUnmounted(() => {
    cancel()
  })

  if (immediate) {
    run()
  }

  return {
    data,
    loading,
    error,
    run,
    cancel
  }
}

/**
 * 分页请求Hook
 */
export function usePagination(requestFn, options = {}) {
  const {
    pageSize = 10,
    immediate = true,
    ...restOptions
  } = options

  const currentPage = ref(1)
  const pageSizeRef = ref(pageSize)
  const total = ref(0)
  const list = ref([])
  const searchKeyword = ref('')

  const { data, loading, run, ...rest } = useRequest(
    (page = currentPage.value, size = pageSizeRef.value, keyword = searchKeyword.value) =>
      requestFn({ page, pageSize: size, search: keyword }),
    {
      immediate: false,
      onSuccess: (res) => {
        list.value = res.list
        total.value = res.total
        restOptions.onSuccess?.(res)
      },
      ...restOptions
    }
  )

  const reload = () => {
    currentPage.value = 1
    run(1, pageSizeRef.value, searchKeyword.value)
  }

  const changePage = (page) => {
    currentPage.value = page
    run(page, pageSizeRef.value, searchKeyword.value)
  }

  const changePageSize = (size) => {
    pageSizeRef.value = size
    reload()
  }

  const handleSearch = (keyword) => {
    searchKeyword.value = keyword
    reload()
  }

  if (immediate) {
    reload()
  }

  return {
    list,
    loading,
    currentPage,
    pageSize: pageSizeRef,
    total,
    searchKeyword,
    reload,
    changePage,
    changePageSize,
    handleSearch,
    ...rest
  }
}
